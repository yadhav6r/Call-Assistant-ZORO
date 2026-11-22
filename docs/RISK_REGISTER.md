# Risk register

| Risk | Why it matters | Mitigation / next action | State |
|---|---|---|---|
| Telephony provider/region not selected | Real-time number availability, media streaming, latency, and cost vary | Confirm target country/region and compare official provider capabilities before integration | Open |
| Recording/transcription consent is jurisdiction-dependent | May create legal and trust issues | Keep recording disabled by default; establish consent and retention policy before production | Open |
| AI response can disclose or promise too much | Caller speech may manipulate model behavior | Enforce deterministic policy, approved-context retrieval, validation, audit, and safe fallback | Required design |
| No PRD was supplied | Product journeys and acceptance details are incomplete | Use supplied TRD/master prompt as working scope; reconcile once PRD is available | Open |
| No project code was present | Existing work cannot be preserved or compared | Scaffold from the brief; update plan as features are implemented | Resolved for initial setup |
