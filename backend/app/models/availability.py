from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AvailabilityState(Base):
    __tablename__ = "availability_states"
    __table_args__ = (
        CheckConstraint(
            "mode IN ('available', 'busy', 'meeting', 'sleeping', 'driving', 'dnd', 'emergency')",
            name="ck_availability_states_mode",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    mode: Mapped[str] = mapped_column(String, nullable=False, server_default="available")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    routing_policy: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
