from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import AvailabilityState
from app.security import AuthContext, get_auth_context

router = APIRouter(prefix="/api/v1/availability", tags=["availability"])
AvailabilityMode = Literal[
    "available", "busy", "meeting", "sleeping", "driving", "dnd", "emergency"
]


class AvailabilityResponse(BaseModel):
    mode: AvailabilityMode
    version: int
    synchronized_at: datetime


class AvailabilityUpdate(BaseModel):
    mode: AvailabilityMode
    expected_version: int = 0


@router.get("", response_model=AvailabilityResponse)
async def get_availability(
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> AvailabilityResponse:
    state = await db.get(AvailabilityState, context.user.id)
    if state is None:
        state = AvailabilityState(user_id=context.user.id)
        db.add(state)
        await db.commit()
        await db.refresh(state)
    return AvailabilityResponse(
        mode=state.mode, version=state.version, synchronized_at=state.updated_at
    )


@router.put("", response_model=AvailabilityResponse)
async def set_availability(
    body: AvailabilityUpdate,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> AvailabilityResponse:
    state = await db.scalar(
        select(AvailabilityState)
        .where(AvailabilityState.user_id == context.user.id)
        .with_for_update()
    )
    if state is None:
        if body.expected_version != 0:
            raise HTTPException(status_code=409, detail="Availability changed; reload and retry")
        state = AvailabilityState(user_id=context.user.id, mode=body.mode, version=1)
        db.add(state)
    else:
        if state.version != body.expected_version:
            raise HTTPException(status_code=409, detail="Availability changed; reload and retry")
        state.mode = body.mode
        state.version += 1
    try:
        await db.commit()
        await db.refresh(state)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Availability changed; reload and retry") from None
    return AvailabilityResponse(
        mode=state.mode, version=state.version, synchronized_at=state.updated_at
    )

