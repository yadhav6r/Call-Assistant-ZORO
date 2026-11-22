"""Provision the one allowed production owner from a one-time secret."""

import asyncio
import os
from datetime import UTC, datetime

from sqlalchemy import select, text

from app.config import get_settings
from app.database import create_database_engine, create_session_factory
from app.models import AuthSession, User
from app.security import password_hash


async def provision_owner() -> None:
    settings = get_settings()
    if settings.app_env.lower() != "production" or settings.owner_email is None:
        raise RuntimeError("Owner provisioning requires production settings and ZORO_OWNER_EMAIL.")

    initial_password = os.environ.get("ZORO_BOOTSTRAP_PASSWORD", "")
    reset_existing = os.environ.get("ZORO_BOOTSTRAP_RESET", "false").lower() == "true"
    if len(initial_password) < 20:
        raise RuntimeError("Set a one-time ZORO_BOOTSTRAP_PASSWORD with at least 20 characters.")

    engine = create_database_engine(settings)
    factory = create_session_factory(engine)
    try:
        async with factory() as db, db.begin():
            # Prevent two first-time bootstrap jobs from creating concurrent owners.
            await db.execute(text("SELECT pg_advisory_xact_lock(740056)"))
            users = list(await db.scalars(select(User).with_for_update()))
            owner_email = str(settings.owner_email).lower()
            if users:
                if len(users) == 1 and users[0].email == owner_email:
                    if reset_existing:
                        users[0].password_hash = password_hash.hash(initial_password)
                        sessions = list(
                            await db.scalars(
                                select(AuthSession).where(AuthSession.user_id == users[0].id)
                            )
                        )
                        for session in sessions:
                            session.revoked_at = session.revoked_at or datetime.now(UTC)
                    return
                raise RuntimeError(
                    "The database already contains an account. Refusing to add or replace an owner."
                )
            db.add(
                User(
                    email=owner_email,
                    password_hash=password_hash.hash(initial_password),
                    display_name=owner_email.split("@", 1)[0],
                    preferred_language="en",
                    timezone="Asia/Kolkata",
                )
            )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(provision_owner())
