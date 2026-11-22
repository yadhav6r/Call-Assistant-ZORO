from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LoginAttempt(Base):
    __tablename__ = "login_attempt_limits"
    __table_args__ = (Index("ix_login_attempt_limits_window", "window_started_at"),)

    bucket_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
