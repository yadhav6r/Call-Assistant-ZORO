# Product brief (from supplied handoff documents)

## Product
ZORO is an Android-first personal AI communication assistant. The Android app is the owner's control plane. Calls are handled in the cloud when deliberately routed to ZORO; the system discloses that it is AI, answers only within owner-configured permissions, and returns call summaries and follow-up items.

## V1
Android onboarding/authentication, availability modes, contacts and caller rules, dedicated programmable inbound number, transparent AI disclosure, real-time voice conversation with interruptions, intent and urgency handling, policy-controlled responses, safe fallback/escalation, call metadata, consent-aware transcription/optional recording, post-call summary/actions, push notifications, searchable history, approval workflow, audit, and privacy/data controls.

## Architecture
Kotlin/Jetpack Compose Android control plane. Python/FastAPI backend for owner-scoped APIs, signed telephony webhooks, policy decisions, AI sessions, persistence and notifications. PostgreSQL is the system of record; Redis/worker for async work where useful. Telephony and AI vendors sit behind adapters.

## Guardrails
Never impersonate the owner or clone their voice. Identify as an AI assistant. Treat caller content as untrusted. The LLM does not authorize actions. Deny sensitive disclosures and binding commitments without suitable verification and owner approval. Recording is disabled by default pending consent and retention policy. Do not claim arbitrary native SIM-call audio access or emergency dispatch.

## Decisions captured
Target region for future feasibility research: India. Development telephony: mock only; real provider and number decision later. Other open decisions include Android device/version, language/voice, recording/transcription/retention, escalation contacts, hosting region and budget.

## Source note
Based on the supplied `PRD.md`, `TRD.md`, and `MASTER_CODEX_PROMPT.md`. These remain requirements references; this summary is working project memory.
