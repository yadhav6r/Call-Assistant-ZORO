from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.api import (
    availability_router,
    auth_router,
    contacts_router,
    profile_router,
    simulated_calls_router,
)
from app.config import get_settings
from app.database import create_database_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_database_engine(get_settings())
    app.state.db_engine = engine
    app.state.db_session_factory = create_session_factory(engine)
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="ZORO API",
    version="0.2.0",
    description="Owner control plane and webhook API for ZORO.",
    lifespan=lifespan,
)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(availability_router)
app.include_router(contacts_router)
app.include_router(simulated_calls_router)


@app.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    """Process liveness only; this does not imply dependencies are ready."""
    return {"status": "ok"}


@app.get("/ready", tags=["operations"])
async def ready() -> dict[str, str]:
    """Readiness check for the current database dependency."""
    engine: AsyncEngine = app.state.db_engine
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is unavailable") from None
    return {"status": "ready"}
