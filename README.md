# ZORO

ZORO is an Android-first personal AI communication assistant. The Android app is the owner's control panel; a cloud backend handles calls routed to ZORO, applies explicit owner policies, and returns call records and follow-up items.

## Project status

Phase 0 discovery is documented in [docs/PHASE_0_DISCOVERY.md](docs/PHASE_0_DISCOVERY.md). Phases 1–3 are implemented; PostgreSQL/Redis are healthy locally, migrations are applied through head, and the API health/readiness checks pass. Phase 2 includes development-only owner APIs, Android sign-in/dashboard, availability and contacts. Phase 3 adds a text-only mock conversation screen and owner-scoped event persistence; no calls or live AI are used. End-to-end app walkthrough remains. App setup is documented in [android/README.md](android/README.md); phase notes are in `docs/`.

## Development direction

Use mock telephony while building and exercising the conversation pipeline. Real provider and number selection is deferred; India is the region to research when that choice is resumed. The first real-call route should use a dedicated programmable number after provider feasibility is confirmed.

## Backend setup

From `backend/`: create a virtual environment, install `python -m pip install -e ".[dev]"`, copy `.env.example` to `.env`, start services with `docker compose -f compose.yaml up -d`, run `alembic upgrade head`, then start `uvicorn app.main:app --reload`. `/health` checks process liveness; `/ready` checks PostgreSQL. Redis is present for future jobs and is not currently used.

## Android setup

Open `android/` in Android Studio with JDK 17 or newer. The default debug URL points to the backend on the Android emulator (`10.0.2.2:8000`). For details, including physical-device URL overrides and release HTTPS requirements, see [android/README.md](android/README.md).

The backend currently refuses non-development configuration because email verification and production secret handling are not implemented. Do not expose this scaffold as a production service.

## Product guardrails

- Identify as an AI assistant; never impersonate the owner or clone their voice.
- Do not assume an ordinary Android app can capture arbitrary SIM-call audio.
- Keep recording disabled by default until consent and retention behavior are defined.
- The server policy engine, not the language model, authorizes disclosures and actions.
- Sensitive and binding requests require denial, owner approval, or escalation under policy.
