# Phase 0 — repository and feasibility discovery

**Status:** Complete for local discovery; external provider feasibility remains open.

## 1. Existing project summary

The workspace was initially empty apart from generated `work/` and `outputs/` folders and had no Git repository or existing app code. A preliminary backend scaffold now exists: FastAPI app, typed settings, async SQLAlchemy engine setup, local PostgreSQL/Redis Compose services, and `/health` and `/ready` routes. These are groundwork only; they have not been run or validated.

## 2. Source requirements reviewed

- `PRD.md` is the product baseline: personas, goals, v1 scope, functional/non-functional requirements, journeys, and release acceptance criteria.
- `TRD.md` is the engineering baseline: Android/backend stack, data model, API inventory, orchestration, telephony, security, operations, and phased implementation.
- `MASTER_CODEX_PROMPT.md` is a workflow handoff for repository inspection and incremental delivery. It is treated as project guidance, not as authority to override the owner's current request.
- The supplied README describes the handoff pack and says to inspect before implementation. Its reference to the absent PRD is resolved by adding the supplied PRD here as `docs/PRD.md`.

## 3. Scope and requirements gaps

V1 is an Android owner control plane plus cloud call service for calls deliberately routed to ZORO. Must-haves include authentication, availability modes, contacts/rules, dedicated-number inbound calls, clear AI disclosure, natural voice turns and interruption, policy-gated answers, safe fallback/escalation, call lifecycle, consent-aware transcripts, summaries/actions, push notifications, searchable history, approvals, audit, export/deletion/retention.

P1 integrations (calendar, SMS, WhatsApp Business, email), additional languages, and digest should follow a reliable P0 call path. Explicit non-goals include SIM audio capture, impersonation/voice cloning, secret recording, autonomous financial/legal commitments, emergency dispatch, and unofficial WhatsApp automation.

Open product/operational choices: Android model/version, provider/account/region, languages/voice, recording/transcription policy and retention, escalation contacts, hosting region/budget. Owner selected **India as the target region for future feasibility research** and **mock telephony for development; real-call routing/provider decision later**. This does not settle provider availability or legal requirements.

## 4. Feasibility risks

- Real-time telephony and media streaming depend on provider availability in the target country, number types, network latency, and pricing. Verify against current official provider documentation before selecting a vendor.
- Recording and transcription obligations depend on jurisdictions and provider terms. Keep recording disabled by default until policy and consent behavior are settled.
- Android cannot be assumed to access arbitrary SIM call audio; dedicated programmable number remains the initial real-call route.
- Low-latency STT/LLM/TTS, barge-in, and safe fallback need end-to-end measurements; architecture diagrams do not establish feasibility or quality.
- AI must not authorize its own actions. Policy checks, approval binding, tenant isolation, and audit are security-critical.
- The PRD's 99.5% availability and summary-rate figures are targets, not measured service levels.

## 5. Proposed architecture and data flow

Android (Kotlin/Compose) authenticates to the FastAPI API and manages owner profile, mode, contacts, calls, approvals, and privacy controls. Telephony provider sends signed webhooks to backend; the backend validates signature and idempotency, creates/updates the call record, resolves owner/mode/contact policy, then attaches the provider media stream to a session gateway. The session pipeline performs STT, intent/urgency classification, approved-context retrieval, structured candidate generation, schema validation, deterministic policy decision, then TTS only for allowed responses. On call end, workers create summary/actions and notifications. PostgreSQL is authoritative; Redis is for cache/queues/rate limits as warranted; FCM delivers owner notifications. Provider-specific services stay behind adapters.

## 6. Data model and migration plan

The TRD ERD identifies: users, devices, contacts, availability rules, agent policies, calls, conversations, conversation events, transcript segments, summaries, action items, commitments, memory entries, approval requests, notifications, audit logs, and provider events.

Migration sequence: (1) users/devices/auth sessions; (2) contacts, availability, and policies; (3) calls, conversations, provider events, and audit; (4) transcripts, summaries, actions, commitments, approvals, notifications; (5) memory/embeddings if semantic retrieval is justified. Use UUIDs, UTC `TIMESTAMPTZ`, foreign keys, owner scoping, indexes, Alembic migrations, and retention-aware separation of audio/text/metadata. Do not store raw audio by default.

## 7. API route inventory

The source TRD specifies `/api/v1`: auth register/login/refresh/logout; profile GET/PATCH; availability GET/PUT; contacts list/create/detail/update/delete; calls list/detail/transcript/events; actions list/update/approve/reject; approvals list/approve/reject; memory list/create/delete; notifications list/mark-read; daily report; telephony inbound/status/consent webhooks; app voice WebSocket and authenticated owner event WebSocket. Owner routes require owner-scoped auth; provider hooks require signature checks. Lists need pagination; mutations need validation/idempotency where appropriate; errors carry server correlation IDs.

## 8. Security and privacy model

Treat caller content, retrieved records, and model/tool output as untrusted. Derive owner identity from auth context, never request payload. Verify signed webhooks and deduplicate events. Enforce strict tenant scope at service/repository level. Use short-lived tokens with refresh rotation, secure Android storage, backend secrets management, rate limits, TLS, encryption at rest, audit trails, redacted logs, least-privilege tools, exact-payload expiring approvals, consent-aware retention, and tested export/deletion. Caller ID is not identity proof. Fail closed on sensitive disclosures and binding requests.

## 9. Phased implementation plan

0. **Discovery (complete):** inspect workspace/specs, record scope, risks, data/API design, first slice, and owner decisions.
1. **Foundation (in progress):** backend shell, validated config, DB/migrations, health/readiness, Docker development setup and CI.
2. **Owner control plane:** auth/profile/mode/contacts plus Android onboarding/dashboard and sync state.
3. **Simulated conversation:** text/mock telephony, session lifecycle, structured candidate response, deterministic policy, event persistence.
4. **Real telephony:** verify India provider/region capabilities, configure a dedicated number, signature-checked webhooks, bidirectional media, fallback and controlled real-call validation.
5. **Post-call workflow:** consent-aware transcript policy, summary/actions, approvals, FCM and call detail/search.
6. **Hardening/release:** security/tenant isolation, costs/quotas, retention/export/deletion, resilience, monitoring, backup/restore, Android release preparation.

## 10. First vertical slice and acceptance

First vertical slice: a runnable backend health/readiness service with explicit configuration and a local database dependency. Acceptance: process liveness responds independently; readiness checks PostgreSQL and returns unavailable when the DB cannot be reached; settings come from validated environment configuration; no provider secrets or real credentials are required. The current scaffold aims at this slice but is **not yet verified**.

## 11. Immediate next work

Finish foundation by adding migrations and configuration documentation, then validate the local service only when explicitly asked to run checks. Keep mock telephony clearly labeled. Before selecting a real provider or enabling recording, confirm country/provider-specific facts and the relevant owner policies.
