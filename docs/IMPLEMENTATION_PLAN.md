# Implementation plan

## Phase 0 — discovery (complete)
Reviewed the supplied PRD/TRD/master prompt and workspace. Captured scope, risks, architecture/data flow, data model/migration sequence, API inventory, threat model, phases, and first slice in [PHASE_0_DISCOVERY.md](PHASE_0_DISCOVERY.md). Target research region is India; telephony remains mock in development while provider/number choice is deferred.

## Phase 1 — backend foundation (implemented and locally validated)
FastAPI shell, typed environment settings, database readiness, SQLAlchemy models, Alembic migrations, local PostgreSQL/Redis services, lint workflow, and setup documentation. On 2026-11-22, PostgreSQL/Redis were confirmed healthy, migrations were applied through head, and `/health` and `/ready` returned `ok` and `ready`. Details: [PHASE_1_FOUNDATION.md](PHASE_1_FOUNDATION.md).

## Phase 2 — owner control plane (implemented; validation pending)
Implemented development registration and auth/session endpoints, plus a single-owner production mode with public signup disabled, one-time owner provisioning, production secret checks, database-backed login throttling, profile/availability/contacts APIs, and Android Compose sign-in/dashboard and contact management. Email verification, push registration, session/device controls, and production validation remain. Details: [PHASE_2_CONTROL_PLANE.md](PHASE_2_CONTROL_PLANE.md).

## Phase 3 — simulated conversation (implemented; basic runtime ready)
Owner-scoped text simulation endpoints and Android screen, call/event persistence, AI disclosure, structured fixed response candidates, deterministic policy metadata, and an allowlist with no external action tools. Migration `0003_simulated_calls` is applied and API health/readiness pass. The complete simulated-call flow still needs an app-level walkthrough. No model inference or real telephony is used. Details: [PHASE_3_SIMULATED_CONVERSATION.md](PHASE_3_SIMULATED_CONVERSATION.md).

## Phase 4 — real telephony (in progress; not live)
The provider research points to Exotel Voicebot/AgentStream as the first candidate: it supports bidirectional WebSocket audio for inbound call flows. A first Exotel-to-OpenAI Realtime audio relay is implemented behind `ZORO_LIVE_CALLS_ENABLED=false`, with Basic Authentication, English/Kannada instructions, PCM format checks, interruption clearing and a five-minute call limit. Private single-owner production authentication is implemented with a one-time bootstrap job, disabled production signup, production secret validation, and PostgreSQL-backed login throttling. Neither the auth flow nor call relay has been deployed or validated in cloud. Number eligibility, KYC, streaming access and price still need confirmation from Exotel. See [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md).

## Phase 5 — post-call workflow
Consent-aware records, summaries/actions/commitments, approvals, FCM, call detail and search.

## Phase 6 — hardening and release
Tenant isolation, prompt-injection and replay controls, quotas/costs, deletion/retention/export, monitoring, resilience, backup/restore and Android release readiness.

