from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import AvailabilityState, Contact, ConversationEvent, SimulatedCall
from app.security import AuthContext, get_auth_context
from app.services.mock_conversation import (
    AI_DISCLOSURE,
    evaluate_candidate,
    propose_response,
)

router = APIRouter(prefix="/api/v1/simulated-calls", tags=["simulated calls"])


class SimulatedCallCreate(BaseModel):
    caller_name: str | None = Field(default=None, max_length=120)
    caller_phone_e164: str | None = Field(default=None, min_length=8, max_length=16)

    @field_validator("caller_phone_e164")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and (not value.startswith("+") or not value[1:].isdigit()):
            raise ValueError("Phone number must use E.164 format, for example +919876543210")
        return value


class TurnCreate(BaseModel):
    text: str = Field(min_length=1, max_length=4000)

    @field_validator("text")
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sequence: int
    speaker: str
    content: str
    policy: dict
    created_at: datetime


class CallResponse(BaseModel):
    id: UUID
    channel: str
    status: str
    caller_name: str | None
    caller_phone_e164: str | None
    contact_name: str | None
    availability_mode: str
    started_at: datetime
    ended_at: datetime | None
    events: list[EventResponse]


async def load_call(db: AsyncSession, user_id: UUID, call_id: UUID) -> tuple[SimulatedCall, list[ConversationEvent]]:
    call = await db.scalar(
        select(SimulatedCall).where(SimulatedCall.id == call_id, SimulatedCall.user_id == user_id)
    )
    if call is None:
        raise HTTPException(status_code=404, detail="Simulated call not found")
    events = list(
        await db.scalars(
            select(ConversationEvent)
            .where(ConversationEvent.call_id == call.id)
            .order_by(ConversationEvent.sequence)
        )
    )
    return call, events


async def render_call(db: AsyncSession, call: SimulatedCall) -> CallResponse:
    contact_name = None
    if call.contact_id is not None:
        contact_name = await db.scalar(select(Contact.display_name).where(Contact.id == call.contact_id))
    events = list(
        await db.scalars(
            select(ConversationEvent)
            .where(ConversationEvent.call_id == call.id)
            .order_by(ConversationEvent.sequence)
        )
    )
    return CallResponse(
        id=call.id,
        channel=call.channel,
        status=call.status,
        caller_name=call.caller_name,
        caller_phone_e164=call.caller_phone_e164,
        contact_name=contact_name,
        availability_mode=call.availability_mode,
        started_at=call.started_at,
        ended_at=call.ended_at,
        events=[EventResponse.model_validate(event) for event in events],
    )


@router.post("", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def start_call(
    body: SimulatedCallCreate,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> CallResponse:
    availability = await db.get(AvailabilityState, context.user.id)
    caller_contact = None
    if body.caller_phone_e164:
        caller_contact = await db.scalar(
            select(Contact).where(
                Contact.user_id == context.user.id,
                Contact.phone_e164 == body.caller_phone_e164,
            )
        )
    call = SimulatedCall(
        user_id=context.user.id,
        caller_name=body.caller_name or (caller_contact.display_name if caller_contact else None),
        caller_phone_e164=body.caller_phone_e164,
        contact_id=caller_contact.id if caller_contact else None,
        availability_mode=availability.mode if availability else "available",
    )
    db.add(call)
    await db.flush()
    disclosure_policy = {
        "decision": "allow",
        "intent": "ai_disclosure",
        "urgency": "normal",
        "proposed_action": "none",
        "allowed_actions": ["record_message"],
        "action_allowed": True,
    }
    db.add(
        ConversationEvent(
            call_id=call.id,
            sequence=1,
            speaker="assistant",
            content=AI_DISCLOSURE,
            policy=disclosure_policy,
        )
    )
    await db.commit()
    await db.refresh(call)
    return await render_call(db, call)


@router.get("", response_model=list[CallResponse])
async def list_calls(
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[CallResponse]:
    calls = list(
        await db.scalars(
            select(SimulatedCall)
            .where(SimulatedCall.user_id == context.user.id)
            .order_by(SimulatedCall.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return [await render_call(db, call) for call in calls]


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: UUID,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> CallResponse:
    call, _ = await load_call(db, context.user.id, call_id)
    return await render_call(db, call)


@router.post("/{call_id}/turns", response_model=CallResponse)
async def add_turn(
    call_id: UUID,
    body: TurnCreate,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> CallResponse:
    call = await db.scalar(
        select(SimulatedCall)
        .where(SimulatedCall.id == call_id, SimulatedCall.user_id == context.user.id)
        .with_for_update()
    )
    if call is None:
        raise HTTPException(status_code=404, detail="Simulated call not found")
    if call.status != "active":
        raise HTTPException(status_code=409, detail="This simulated call has already ended")
    event_count = await db.scalar(
        select(func.count()).select_from(ConversationEvent).where(ConversationEvent.call_id == call.id)
    )
    if event_count >= 201:
        raise HTTPException(status_code=409, detail="This simulation reached its 100-turn limit")

    candidate = propose_response(body.text)
    decision = evaluate_candidate(candidate)
    if not decision["action_allowed"]:
        response_text = "I can’t perform that action. I can take a message for the owner instead."
    else:
        response_text = candidate.proposed_response
    caller_sequence = event_count + 1
    db.add_all(
        [
            ConversationEvent(
                call_id=call.id,
                sequence=caller_sequence,
                speaker="caller",
                content=body.text,
                policy={"decision": "input", "intent": candidate.intent},
            ),
            ConversationEvent(
                call_id=call.id,
                sequence=caller_sequence + 1,
                speaker="assistant",
                content=response_text,
                policy=decision,
            ),
        ]
    )
    await db.commit()
    return await render_call(db, call)


@router.post("/{call_id}/end", response_model=CallResponse)
async def end_call(
    call_id: UUID,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> CallResponse:
    call = await db.scalar(
        select(SimulatedCall)
        .where(SimulatedCall.id == call_id, SimulatedCall.user_id == context.user.id)
        .with_for_update()
    )
    if call is None:
        raise HTTPException(status_code=404, detail="Simulated call not found")
    if call.status == "active":
        call.status = "ended"
        call.ended_at = datetime.now(UTC)
        await db.commit()
    return await render_call(db, call)
