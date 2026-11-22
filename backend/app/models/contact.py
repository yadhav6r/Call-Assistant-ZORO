from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("user_id", "phone_e164", name="uq_contacts_user_phone"),
        CheckConstraint(
            "trust_level IN ('unverified', 'known', 'verified')",
            name="ck_contacts_trust_level",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_e164: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, server_default="unknown")
    notes: Mapped[str | None] = mapped_column(String)
    trust_level: Mapped[str] = mapped_column(String, nullable=False, server_default="unverified")
    handling_rule: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
