from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import Contact
from app.security import AuthContext, get_auth_context

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])
TrustLevel = Literal["unverified", "known", "verified"]


class ContactCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    phone_e164: str = Field(min_length=8, max_length=16)
    category: str = Field(default="unknown", min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=2000)
    trust_level: TrustLevel = "unverified"
    handling_rule: dict = Field(default_factory=dict)

    @field_validator("phone_e164")
    @classmethod
    def validate_phone_e164(cls, value: str) -> str:
        if not value.startswith("+") or not value[1:].isdigit():
            raise ValueError("Phone number must be in E.164 format, for example +14155552671")
        return value


class ContactUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    phone_e164: str | None = Field(default=None, min_length=8, max_length=16)
    category: str | None = Field(default=None, min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=2000)
    trust_level: TrustLevel | None = None
    handling_rule: dict | None = None

    @field_validator("phone_e164")
    @classmethod
    def validate_phone_e164(cls, value: str | None) -> str | None:
        if value is not None and (not value.startswith("+") or not value[1:].isdigit()):
            raise ValueError("Phone number must be in E.164 format, for example +14155552671")
        return value


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    phone_e164: str
    category: str
    notes: str | None
    trust_level: TrustLevel
    handling_rule: dict
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=list[ContactResponse])
async def list_contacts(
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Contact]:
    return list(
        await db.scalars(
            select(Contact)
            .where(Contact.user_id == context.user.id)
            .order_by(Contact.display_name)
            .limit(limit)
            .offset(offset)
        )
    )


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> Contact:
    contact = Contact(user_id=context.user.id, **body.model_dump())
    db.add(contact)
    try:
        await db.commit()
        await db.refresh(contact)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This phone number is already in contacts") from None
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> Contact:
    contact = await db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == context.user.id)
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    body: ContactUpdate,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> Contact:
    contact = await db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == context.user.id)
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is not None or key == 'notes':
            setattr(contact, key, value)
    try:
        await db.commit()
        await db.refresh(contact)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This phone number is already in contacts") from None
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    context: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> Response:
    contact = await db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == context.user.id)
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(contact)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


