# Phase 3 — simulated conversation

**Status:** Implemented; Android compile and Python syntax compilation passed. Migration is applied and the API is running; end-to-end simulation flow still needs an app-level walkthrough.

## Included

- Authenticated, owner-scoped endpoints to create, list, read, turn, and end text-simulated calls.
- A development-only call record captures caller metadata, availability snapshot, status, and timestamps.
- Ordered conversation events persist caller and assistant text plus structured policy decisions.
- Each simulation opens with a clear statement that ZORO is an AI assistant and that the interaction is a text simulation.
- Fixed response candidates classify ordinary messages, private-information requests, availability questions, commitments, and urgent messages.
- A deterministic policy allowlist permits only recording a message for owner review. It cannot send messages, make bookings, spend money, accept terms, or contact emergency services.
- Android `Simulate` tab supports starting a mock conversation, sending turns, reviewing policy labels, ending the session, and opening another simulation.
- Alembic migration `0003_simulated_calls` creates the call and event tables.

## API

- `POST /api/v1/simulated-calls`
- `GET /api/v1/simulated-calls`
- `GET /api/v1/simulated-calls/{call_id}`
- `POST /api/v1/simulated-calls/{call_id}/turns`
- `POST /api/v1/simulated-calls/{call_id}/end`

All routes require the owner's bearer token. Lookup and mutation are scoped to the authenticated owner.

## Limitations and next work

- This is a text simulation, not a telephony adapter or live voice call. It uses no external AI model.
- Availability is recorded on the call but does not yet alter the conversation policy.
- Raw text turns are persisted for this development simulation. Recording/transcription consent and retention controls must be designed before real calls.
- Call history, detail search, summaries, and Android review of ended calls remain for Phase 5.
- Run database migrations and start the backend before using the Android simulation screen. Development authentication remains unsuitable for production.

## Validation

No automated tests were added or run. Android `assembleDebug` completed successfully; Python syntax compilation passed; migrations were applied; and the API reports healthy/readiness status. The simulated-call endpoints have not yet been walked through end-to-end in the app.
