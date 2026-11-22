# Phase 2 — owner control plane

**Status:** Backend APIs and initial Android sign-in/dashboard scaffold are implemented. Backend startup and database readiness are confirmed; authentication and owner API flows still need an app-level walkthrough.

## Backend endpoints

- `POST /api/v1/auth/register` — development-only account creation with Argon2 password hashing.
- `POST /api/v1/auth/login` — short-lived signed access token plus opaque refresh token.
- `POST /api/v1/auth/refresh` — rotates refresh token and issues a new access token.
- `POST /api/v1/auth/logout` — revokes the active session; authenticated requests check revocation.
- `GET/PATCH /api/v1/profile` — owner-scoped profile view and updates.
- `GET/PUT /api/v1/availability` — seven availability modes, persisted version and optimistic version check.
- `GET/POST /api/v1/contacts`, `GET/PATCH/DELETE /api/v1/contacts/{id}` — owner-scoped contact directory with E.164 number validation and per-owner phone uniqueness.

## Android slice

Native Kotlin/Compose shell with create-account/sign-in, encrypted token storage using Android Keystore, automatic refresh on expired access tokens, owner profile display, availability sync/version updates, contacts list/add/edit/delete, and sign-out. App setup and API base URL notes are in [android/README.md](../android/README.md).

## Security boundaries and limitations

- Passwords are Argon2-hashed; refresh tokens are stored only as SHA-256 digests and rotate on use.
- Access tokens expire and are checked against a non-revoked, unexpired server session on each protected request.
- Every profile, mode, and contact query is scoped to the authenticated owner.
- Backend configuration currently must be `development`: it refuses non-development configuration until email verification and production secret handling are implemented. Registration currently does not verify email.
- Android debug allows cleartext for local emulator development; release configuration rejects cleartext and must use HTTPS.
- Rate limiting, account recovery, verified email, device/session management UI, audit events, push token registration, and call history are not implemented in this slice.
- Contact handling rules are stored as owner data only; they are not yet interpreted by a call agent.

## Database

Migration `0002_owner_control_plane` adds password hashes, auth sessions, availability state, and contacts. Apply with `alembic upgrade head` after Phase 1 setup.

## Next Phase 2 slice

Add push token registration, session/device controls, and account verification/recovery design. Then validate migrations and run the backend and app before calling Phase 2 complete.

## Validation

No tests, lint, database migration, API smoke check, or Android build has been run. The current implementation is not runtime-verified.

