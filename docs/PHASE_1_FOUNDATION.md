# Phase 1 — backend foundation

**Status:** Implemented and locally validated on 2026-11-22.

## Included

- FastAPI app with separate `/health` liveness and `/ready` PostgreSQL dependency check.
- Pydantic settings read from `ZORO_` environment variables; defaults are local development settings.
- Async SQLAlchemy engine lifecycle.
- SQLAlchemy `users` and `devices` models, aligned with the supplied TRD's initial owner/device schema.
- Alembic async migration environment and first migration for owner/device tables.
- Compose services for PostgreSQL 16 and Redis 7. The API currently uses PostgreSQL only.
- GitHub Actions lint workflow using Ruff.
- Local setup and migration steps in the root README.

## Deliberately not included yet

Authentication endpoints/session token flow, owner profile APIs, Android client, domain tables beyond users/devices, Redis worker, AI/telephony adapters, and external provider credentials. These belong to later slices and require additional design decisions.

## Manual startup sequence

From `backend/`: install `.[dev]`, copy `.env.example` to `.env` if needed, run `docker compose -f compose.yaml up -d`, apply `alembic upgrade head`, and run `uvicorn app.main:app --reload`.

## Completion note

PostgreSQL 16 and Redis 7 started as healthy Docker services; Alembic applied migrations through `0003_simulated_calls`; the API started locally and `/health` returned `ok` while `/ready` returned `ready`. No automated tests or lint run was performed. The API and database/cache ports are bound to localhost for development.
