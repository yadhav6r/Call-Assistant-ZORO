from datetime import UTC, datetime, timedelta

from sqlalchemy import case, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LoginAttempt

WINDOW = timedelta(minutes=15)
LOCK_DURATION = timedelta(minutes=15)
EMAIL_FAILURE_LIMIT = 5
IP_FAILURE_LIMIT = 30


async def active_lock_until(
    db: AsyncSession, bucket_hashes: list[str], now: datetime
) -> datetime | None:
    if not bucket_hashes:
        return None
    rows = list(
        await db.scalars(
            select(LoginAttempt).where(LoginAttempt.bucket_hash.in_(bucket_hashes))
        )
    )
    locks = [row.locked_until for row in rows if row.locked_until and row.locked_until > now]
    return max(locks) if locks else None


async def record_failure(
    db: AsyncSession,
    bucket_hash: str,
    threshold: int,
    now: datetime,
) -> None:
    expired = LoginAttempt.window_started_at <= now - WINDOW
    statement = insert(LoginAttempt).values(
        bucket_hash=bucket_hash,
        window_started_at=now,
        failed_attempts=1,
        locked_until=None,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[LoginAttempt.bucket_hash],
        set_={
            "window_started_at": case(
                (expired, now), else_=LoginAttempt.window_started_at
            ),
            "failed_attempts": case(
                (expired, 1), else_=LoginAttempt.failed_attempts + 1
            ),
            "locked_until": case(
                (expired, None),
                (LoginAttempt.failed_attempts + 1 >= threshold, now + LOCK_DURATION),
                else_=LoginAttempt.locked_until,
            ),
        },
    )
    await db.execute(statement)


async def clear_failures(db: AsyncSession, bucket_hashes: list[str]) -> None:
    if bucket_hashes:
        await db.execute(
            delete(LoginAttempt).where(LoginAttempt.bucket_hash.in_(bucket_hashes))
        )


async def prune_old_failures(db: AsyncSession, now: datetime) -> None:
    await db.execute(
        delete(LoginAttempt).where(LoginAttempt.window_started_at < now - timedelta(days=1))
    )


def retry_after_seconds(locked_until: datetime, now: datetime) -> int:
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=UTC)
    return max(1, int((locked_until - now).total_seconds()))
