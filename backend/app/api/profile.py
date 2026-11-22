from fastapi import APIRouter, Depends
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import User
from app.security import AuthContext, get_auth_context

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str
    timezone: str
    preferred_language: str


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=16)


@router.get("", response_model=ProfileResponse)
async def get_profile(context: AuthContext = Depends(get_auth_context)) -> User:
    return context.user


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    body: ProfileUpdate,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> User:
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(context.user, key, value)
    await db.commit()
    await db.refresh(context.user)
    return context.user




