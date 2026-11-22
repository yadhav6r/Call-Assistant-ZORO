from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SimulatedCall(Base):
    __tablename__ = "calls"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'ended')", name="ck_calls_status"),
        CheckConstraint("channel = 'text_simulation'", name="ck_calls_channel"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False, server_default="text_simulation")
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="active")
    caller_name: Mapped[str | None] = mapped_column(String(120))
    caller_phone_e164: Mapped[str | None] = mapped_column(String(16))
    contact_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL")
    )
    availability_mode: Mapped[str] = mapped_column(String(24), nullable=False, server_default="available")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ConversationEvent(Base):
    __tablename__ = "conversation_events"
    __table_args__ = (
        UniqueConstraint("call_id", "sequence", name="uq_conversation_events_call_sequence"),
        CheckConstraint("speaker IN ('assistant', 'caller', 'system')", name="ck_events_speaker"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    call_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    policy: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
