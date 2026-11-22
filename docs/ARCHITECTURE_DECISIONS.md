# Architecture decisions

## 0001 — Cloud backend owns call handling
**Status:** Accepted as the supplied product baseline. The Android app is the owner's control plane; the backend owns telephony webhooks, policy decisions, AI sessions, persistence, and notifications. This permits cloud call handling when the owner's phone is offline.

## 0002 — Dedicated programmable number is the first real-call path
**Status:** Accepted as the supplied baseline. Do not build around capture of arbitrary cellular call audio. Provider and region remain undecided.

## 0003 — LLM does not authorize actions
**Status:** Accepted as a required safety boundary. Model output is a candidate only; a deterministic policy service validates disclosure and action requests.

## 0004 — Start with a minimal FastAPI liveness slice
**Status:** Implemented. `/health` indicates process liveness only and must not imply downstream dependency readiness.

## Pending decisions
Android architecture/module boundaries, auth provider, telephony and AI vendors, deployment region, consent behavior, data retention, languages, and budget are open pending owner/product input.
