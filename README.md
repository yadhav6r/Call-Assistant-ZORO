# ZORO

ZORO is an Android-first personal AI communication assistant. The Android app is the owner's control panel; a cloud backend handles calls routed to ZORO, applies explicit owner policies, and returns call records and follow-up items.

## Project status

Phases 0–3 are implemented for local development. The API, owner control panel, and text-only call simulation work locally; the project has no real phone call handling or live AI yet. See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for progress and [docs/DEPLOYMENT_PLAN.md](docs/DEPLOYMENT_PLAN.md) for the proposed live setup and its remaining requirements.

## Development direction

Use mock telephony while building and exercising the conversation pipeline. The first live candidate is Exotel inbound Voicebot/AgentStream with a dedicated programmable number in India; the owner selected English and Kannada. Provider eligibility, KYC and streaming price are not confirmed. See the deployment plan before configuring a real account.

## Backend setup

From `backend/`: create a virtual environment, install `python -m pip install -e ".[dev]"`, copy `.env.example` to `.env`, start services with `docker compose -f compose.yaml up -d`, run `alembic upgrade head`, then start `uvicorn app.main:app --reload`. `/health` checks process liveness; `/ready` checks PostgreSQL. Redis is present for future jobs and is not currently used.

## Android setup

Open `android/` in Android Studio with JDK 17 or newer. The default debug URL points to the backend on the Android emulator (`10.0.2.2:8000`). For details, including physical-device URL overrides and release HTTPS requirements, see [android/README.md](android/README.md).

The backend supports a private, single-owner production mode with public signup disabled, an owner-provisioning job, required production secrets, and database-backed login throttling. These controls and the Exotel voice relay are implemented but not yet deployed or validated in cloud. Keep `ZORO_LIVE_CALLS_ENABLED=false` until the provider flow is configured and a controlled call succeeds.

## Product guardrails

- Identify as an AI assistant; never impersonate the owner or clone their voice.
- Do not assume an ordinary Android app can capture arbitrary SIM-call audio.
- Keep recording disabled by default until consent and retention behavior are defined.
- The server policy engine, not the language model, authorizes disclosures and actions.
- Sensitive and binding requests require denial, owner approval, or escalation under policy.
