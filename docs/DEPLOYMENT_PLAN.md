# ZORO live deployment plan

## Current state

ZORO is not live yet. The Android app is an owner control panel; its conversation screen is a text simulation. A first Exotel-to-Realtime audio relay is implemented, but it is off by default and has not been tested with Exotel or a real call. The backend supports local development only and deliberately rejects production configuration. No telephony or AI provider is connected, no production database exists, and no cloud deployment has been made.

## Recommended first live architecture

- **Android frontend:** Keep the native Android app. Use Google Play internal testing for private updates once the release is signed and the store requirements are met. Until then, a signed APK can be shared directly for a small personal pilot. There is no separate web frontend in this project.
- **Call provider:** Ask Exotel to confirm a personal-use inbound Exophone in the owner's Indian circle, KYC requirements, and AgentStream/Voicebot streaming access and price. Exotel is the best first candidate because its Voicebot Applet supports bidirectional WebSocket audio. Use a dedicated number first; do not forward the owner's existing SIM until carrier forwarding is separately checked.
- **Live backend:** Google Cloud Run in `asia-south1` (Mumbai), with one minimum instance to reduce cold starts, WebSockets enabled, and a long request timeout. Cloud Run supports WebSockets, but each stream is still limited by the configured request timeout (maximum 60 minutes); the call adapter must handle disconnects and cleanup.
- **Database:** Cloud SQL for PostgreSQL in Mumbai, attached privately to Cloud Run. Keep call metadata and settings only at first. Do not store audio; avoid transcripts until the disclosure, consent, retention, and deletion flow is decided.
- **Secrets:** Google Secret Manager for database credentials, signing key, Exotel credentials, and AI-provider credentials. Never put them in the Android app, repository, image, or logs.
- **AI voice:** An audio-capable service behind a provider adapter. English and Kannada are the first requested languages. Before enabling external audio processing, validate language quality and latency in controlled calls and show a clear AI disclosure before streaming begins.

Cloud Run and Cloud SQL are both available in Mumbai. This setup is not free: Cloud Run with a warm instance, Cloud SQL, phone number/call minutes, Exotel streaming, and AI usage can all incur charges. Put budget alerts and provider-side limits in place before activating calls. Exact telephony-streaming charges need a written Exotel quote; the public Exotel Dabbler price lists ₹9,999 for five months (₹4,999 rental plus ₹5,000 credits) and excludes AgentStream streaming.

## Why not use Render's free tier for real calls

Render's free web service sleeps after 15 minutes without traffic and can take about a minute to wake. Its free PostgreSQL database expires after 30 days and has no backups. An inbound caller should not wait for a sleeping backend to wake, so Render free is suitable only for a temporary mock/demo, not live call handling.

## Required work before a real caller can be connected

1. Replace development-only account setup with production authentication, verified owner access, request throttling, and a recovery path. Keep registration closed until this is done.
2. Validate the Exotel WebSocket auth and media protocol in its sandbox; the current relay handles the live media stream but does not yet create durable call lifecycle records or post-call summaries. Add those, idempotency, and a provider-approved safe fallback before real callers use it.
3. Validate the real-time voice adapter against Exotel's sandbox. It expects Exotel raw PCM16 mono at 24 kHz and relays it to OpenAI Realtime with no sample-rate conversion. The default call limit is five minutes. Test English/Kannada speech recognition, voice quality, interruptions, packet pacing, timeouts and cost with the owner. If Exotel only provisions 8 kHz/16 kHz audio for the chosen account, add and validate resampling before enabling it.
4. Configure the Exotel call flow to disclose that the caller is speaking to an AI and obtain any required consent before the voice stream reaches an external AI service. Keep recording off.
5. Add policy controls so the agent cannot make commitments, disclose private data, make payments, or contact others without owner approval.
6. Provide a caller-facing privacy notice and define retention/deletion before retaining transcripts or summaries.
7. Deploy the API and database to a paid, monitored cloud project; configure HTTPS/WSS, secrets, backups, budget alerts, and a rollback path.
8. Update Android compile/target API from 35 to 36 with a compatible Android Gradle Plugin, review target-SDK behavior changes, point the release build to the deployed HTTPS API, create a signed Android App Bundle, and distribute privately through Play internal testing or a signed APK.
9. Make a controlled test call from a known number, verify the AI disclosure, English/Kannada turns, interruption/failure fallback, metadata and owner view, then enable the number for intended callers.

## External account and spending gates

The repository can be prepared without account credentials. The following steps require the owner's action and explicit cost/account confirmation at that time: create or upgrade cloud billing, create the Exotel account/number and complete KYC, accept provider terms, obtain streaming access, create an AI API key and set a spend cap, create/accept Google Play Console setup, and publish or distribute an app. No such external action has been taken.

## Current deployment artifact

`backend/Dockerfile` packages the API as a non-root container for Cloud Run. It does not run database migrations automatically. Migrations must be executed as a reviewed, one-off release step after the production database is provisioned and before traffic is switched over. The live-call route is `/api/v1/telephony/exotel/stream?sample-rate=24000`; it requires Exotel Basic Authentication and `ZORO_LIVE_CALLS_ENABLED=true`, plus Exotel stream credentials and an AI API key. The default is `false`. Do not enable it or expose the service publicly until consent is configured in the provider flow, production authentication is complete, and the controlled call checks above pass. The application still refuses production mode.

The relay sends call audio to the configured AI provider in real time but does not save audio or transcripts in ZORO. The provider still processes the audio; review its terms, data handling and retention before the first caller is connected. Keep Exotel recording disabled.
