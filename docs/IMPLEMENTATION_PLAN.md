# Implementation plan

## Phase 0 — discovery (complete)
Reviewed the supplied PRD/TRD/master prompt and workspace. Captured scope, risks, architecture/data flow, data model/migration sequence, API inventory, threat model, phases, and first slice in [PHASE_0_DISCOVERY.md](PHASE_0_DISCOVERY.md). Target research region is India; telephony remains mock in development while provider/number choice is deferred.

## Phase 1 — backend foundation (implemented and locally validated)
FastAPI shell, typed environment settings, database readiness, SQLAlchemy models, Alembic migrations, local PostgreSQL/Redis services, lint workflow, and setup documentation. On 2026-11-22, PostgreSQL/Redis were confirmed healthy, migrations were applied through head, and `/health` and `/ready` returned `ok` and `ready`. Details: [PHASE_1_FOUNDATION.md](PHASE_1_FOUNDATION.md).

## Phase 2 — owner control plane (implemented; validation pending)
Implemented development-only auth/session endpoints, profile endpoints, versioned availability state, owner-scoped contacts API, migration `0002_owner_control_plane`, and Android Compose sign-in/dashboard and contacts list/add/edit/delete with encrypted session storage. Email verification, push registration, and session/device controls remain. Details: [PHASE_2_CONTROL_PLANE.md](PHASE_2_CONTROL_PLANE.md).

## Phase 3 — simulated conversation (implemented; basic runtime ready)
Owner-scoped text simulation endpoints and Android screen, call/event persistence, AI disclosure, structured fixed response candidates, deterministic policy metadata, and an allowlist with no external action tools. Migration `0003_simulated_calls` is applied and API health/readiness pass. The complete simulated-call flow still needs an app-level walkthrough. No model inference or real telephony is used. Details: [PHASE_3_SIMULATED_CONVERSATION.md](PHASE_3_SIMULATED_CONVERSATION.md).

## Phase 4 — real telephony
Verify provider and India-region capabilities, then implement dedicated-number signed webhooks, media gateway, timeouts/fallback and controlled real-call validation.

## Phase 5 — post-call workflow
Consent-aware records, summaries/actions/commitments, approvals, FCM, call detail and search.

## Phase 6 — hardening and release
Tenant isolation, prompt-injection and replay controls, quotas/costs, deletion/retention/export, monitoring, resilience, backup/restore and Android release readiness.

