# ZORO --- Product Requirements Document (PRD)

**Version:** 1.0\
**Status:** Baseline for implementation\
**Product:** Personal AI Communication Agent\
**Primary client:** Android\
**Execution model:** Android control plane + cloud telephony/AI backend

------------------------------------------------------------------------

## 1. Executive summary

ZORO is an Android-first personal AI communication agent. It handles
calls deliberately routed to a ZORO-controlled telephony endpoint,
transparently identifies itself as an AI assistant, gathers caller
requests, answers routine questions using owner-approved information,
escalates sensitive matters, and creates searchable records of
conversations and follow-up actions.

The Android application is the owner's control center. Cloud services
perform call routing, AI inference, conversation orchestration,
persistence and notifications. Therefore, calls can be handled while the
Android phone is asleep or offline, provided the telephony provider and
cloud backend remain operational.

**Important platform boundary:** An ordinary Android app cannot be
assumed to answer arbitrary native SIM calls and access their live
audio. Android call-screening APIs do not provide unrestricted live
call-audio access. The first real-call implementation must use a
dedicated programmable number. Support for the owner's existing SIM
number may be added through carrier/provider-supported conditional call
forwarding after country and carrier compatibility are verified.

## 2. Problem statement

When the owner is sleeping, in a meeting, studying, driving or otherwise
unavailable, callers may receive no useful response. A missed-call
notification does not explain why the person called, what they
requested, whether they need a callback, or what was agreed.

ZORO provides a transparent AI communication layer that: - answers calls
routed to it; - identifies itself as an AI assistant; - gathers caller
purpose and relevant details; - answers only within configured
permissions; - escalates urgent or sensitive matters; - creates
summaries, tasks and commitments; - notifies the owner according to
priority; - preserves an auditable communication history.

## 3. Vision, principles and success metrics

### 3.1 Vision

A trusted personal communication agent that handles routine
communication without pretending to be the owner or making unauthorized
commitments.

### 3.2 Principles

1.  Owner control: owner defines availability, rules, contacts and
    permissions.
2.  Transparency: caller is told they are speaking with an AI assistant.
3.  Least privilege: agent receives only the data/tools needed for the
    task.
4.  Human oversight: high-impact actions require owner approval.
5.  Reliability: safe fallback is preferable to fabricated answers.
6.  Privacy: recording/transcription follow applicable law, consent and
    provider terms.
7.  Auditability: consequential agent actions are recorded.
8.  Portability: AI and telephony vendors are accessed through adapters.

### 3.3 Initial success metrics (targets to validate)

-   100% of AI-handled calls include AI disclosure.
-   100% of external actions pass server-side policy checks.
-   100% of completed calls produce a call metadata record.
-   At least 95% of completed calls produce a post-call summary
    (excluding provider/system failures).
-   No unauthorized private-data disclosure in security test suite.
-   Owner can view a call summary and action items in Android.
-   Cloud call handling continues when the Android device is offline.

Targets are engineering objectives, not claims of measured performance.

## 4. Goals and non-goals

### 4.1 Goals

-   Native Android application for controlling ZORO.
-   Cloud-based call answering for a dedicated programmable number.
-   Availability modes and caller-specific rules.
-   Natural voice conversations with interruption handling.
-   Contact recognition using authorized records.
-   Approved personal-context retrieval.
-   Call summaries, transcripts where permitted, and action items.
-   Urgency-based notifications.
-   Approval queue for sensitive actions.
-   Searchable call and interaction history.
-   Data export, retention and deletion controls.

### 4.2 Non-goals for v1

-   Secret recording.
-   Impersonating the owner.
-   Deceptive voice cloning.
-   Arbitrary capture of native SIM-call audio.
-   Autonomous financial transactions.
-   Accepting contracts, legal offers or employment terms.
-   Disclosing sensitive personal data to unverified callers.
-   Emergency-service dispatch.
-   Unofficial WhatsApp personal-account automation.
-   Replacing Android default dialer/SMS app unless separately justified
    and policy-compliant.

## 5. Personas and roles

### 5.1 Owner

The sole account owner in v1. Controls availability, contacts, policies,
approvals, data and notifications.

### 5.2 Callers

-   Known personal contact
-   Family member
-   College/work contact
-   Client/business enquiry
-   Unknown caller
-   Configured emergency contact

Callers are not application users by default and receive no access to
owner data.

### 5.3 System roles

-   `OWNER`: full account control.
-   `AGENT`: server-side execution under explicit policies; not a human
    login role.
-   `SERVICE`: telephony, notification and background service
    identities.
-   `CALLER`: untrusted external participant.

## 6. Scope and priorities

### P0 --- first end-to-end release

1.  Android onboarding and authentication.
2.  Availability mode controls.
3.  Contact directory and caller rules.
4.  Dedicated programmable inbound number.
5.  AI disclosure at call start.
6.  Real-time voice conversation.
7.  Intent classification.
8.  Policy-controlled response generation.
9.  Safe fallback and human escalation.
10. Call metadata and lifecycle tracking.
11. Consent-aware transcription and optional recording.
12. Post-call summary.
13. Action-item extraction.
14. Push notifications.
15. Searchable call history and call detail.
16. Approval/rejection of proposed actions.
17. Audit logs.
18. Privacy, retention and deletion settings.

### P1

-   App-based voice conversation with ZORO.
-   Calendar integration with explicit account authorization.
-   Supported SMS workflow.
-   WhatsApp Business Platform integration.
-   Email integration.
-   Additional languages.
-   Daily digest.

### P2

-   Analytics dashboard.
-   Advanced contact/relationship context.
-   Multi-device administration.
-   Configurable workflows.

## 7. Availability modes

  -----------------------------------------------------------------------
  Mode                                Expected behavior
  ----------------------------------- -----------------------------------
  Available                           Follow owner's configured routing
                                      policy

  Busy                                Answer delegated calls and collect
                                      requests

  Meeting                             Handle routine calls; escalate
                                      configured urgent cases

  Sleeping                            Handle delegated calls quietly;
                                      urgent push/approved escalation
                                      only

  Driving                             Handle delegated calls without
                                      requiring owner interaction

  DND                                 Strict caller filtering and
                                      configured allowlist/voicemail
                                      policy

  Emergency                           Apply configured emergency-contact
                                      and escalation policy
  -----------------------------------------------------------------------

Modes are presets mapping to explicit routing, notification and
permission rules. Mode changes must be timestamped and synchronized to
backend. If offline, UI must show whether the change reached the server.
Backend must define a safe default if no fresh mode is available.

## 8. User journeys

### 8.1 First-time setup

1.  Install Android app.
2.  Create account and verify identity.
3.  Review privacy, transcription and recording settings.
4.  Add contacts and caller categories.
5.  Configure availability modes.
6.  Select language and voice.
7.  Connect telephony provider/dedicated number.
8.  Run a controlled test call.
9.  Activate ZORO.

### 8.2 Sleeping-mode call

1.  Owner activates Sleeping Mode.
2.  Android confirms backend synchronization.
3.  Caller dials dedicated ZORO number or verified forwarded number.
4.  Telephony provider sends inbound event.
5.  ZORO identifies itself as AI assistant.
6.  ZORO asks the caller's purpose.
7.  It answers only from permitted context.
8.  It collects details for unresolved requests.
9.  It escalates if configured criteria are met.
10. Call ends; post-call processing runs.
11. Owner receives notification based on urgency.
12. Morning digest lists calls, summaries and pending actions.

### 8.3 Meeting-mode call

1.  Meeting Mode is activated manually or by an authorized calendar
    rule.
2.  Delegated call reaches ZORO.
3.  Routine callers are screened and their requests collected.
4.  Only configured urgent callers/reasons interrupt the owner.
5.  ZORO does not promise a meeting time unless calendar access and
    policy allow it.
6.  Owner reviews summaries and tasks after the meeting.

### 8.4 Callback request

1.  Caller asks for a callback.
2.  ZORO confirms the preferred callback number and reason.
3.  ZORO creates an action item.
4.  Owner receives notification.
5.  Owner marks complete, dismisses, or initiates callback manually.

### 8.5 Sensitive request

1.  Caller requests a financial, legal, confidential or binding action.
2.  ZORO does not execute it.
3.  ZORO collects non-sensitive details where appropriate.
4.  A pending approval or escalation record is created.
5.  Owner decides outside the call or through a verified workflow.

## 9. Functional requirements

### FR-001 Authentication and owner profile

-   Owner can register/login securely.
-   Session tokens are protected.
-   Profile stores display name, timezone, language and preferences.
-   All records are scoped to owner ID.
-   Owner can revoke sessions/devices.

### FR-002 Availability

-   Owner can set a mode manually.
-   Modes may have scheduled start/end times.
-   Backend stores authoritative active mode.
-   Android displays synchronization status.
-   Rules can define caller allowlists and escalation behavior.
-   Mode changes create audit events.

### FR-003 Contacts

-   Owner can add/edit/delete contacts.
-   Contact has name, normalized phone number, category and notes.
-   Contact may have allowed disclosure level and handling rule.
-   Unknown caller must never be treated as a verified identity.
-   Caller ID is a hint, not strong identity proof.

### FR-004 Inbound call handling

-   Accept provider webhook after signature validation.
-   Create unique call/session ID.
-   Retrieve owner routing policy and mode.
-   Connect approved real-time media stream.
-   Play AI disclosure before normal conversation.
-   Support timeout, hang-up, transfer/escalation and fallback.
-   Deduplicate provider webhook events.

### FR-005 Voice conversation

-   Streaming STT and TTS through adapters.
-   Detect end of utterance.
-   Support barge-in.
-   Handle noise, silence and low confidence.
-   Ask for clarification where necessary.
-   Maintain per-call context and bounded conversation history.
-   Respect call duration and cost limits.

### FR-006 AI response and policy

-   Classify intent and urgency.
-   Retrieve only relevant approved memory.
-   Generate structured response/action proposal.
-   Validate schema and policy.
-   Never let LLM itself authorize tools.
-   Return safe fallback if model/provider fails.

### FR-007 Post-call processing

-   Store call lifecycle and provider metadata.
-   Store transcript only when configured and permitted.
-   Create summary, intent, urgency and entities.
-   Extract action items and possible commitments.
-   Mark uncertain extraction for owner review.
-   Run asynchronously after call termination.

### FR-008 Notifications

-   Notify owner of completed calls based on settings.
-   Immediate escalation for configured urgent events.
-   Batch routine events into digest if desired.
-   Include deep link to call detail.
-   Do not put sensitive transcript content on lock-screen by default.

### FR-009 Action items and approvals

-   Action item states: `PENDING`, `APPROVED`, `IN_PROGRESS`,
    `COMPLETED`, `REJECTED`, `CANCELLED`, `EXPIRED`.
-   Owner can approve/reject.
-   Approval must be bound to exact action payload and expire.
-   Approval does not permit a changed payload.
-   Sensitive actions require re-authentication or separate
    confirmation.

### FR-010 Search and reports

-   Search call records by contact, date, status and intent.
-   Filter by availability mode and urgency.
-   Show summary, permitted transcript, actions and audit history.
-   Generate daily/weekly digest.

### FR-011 Privacy and data controls

-   Separate call audio, transcript, summary and metadata.
-   Configurable recording/transcription policy.
-   Retention period configurable by data type.
-   Export owner data.
-   Delete call and associated derived data according to policy.
-   Log deletion requests and completion.
-   Provider retention must be documented separately.

## 10. User interface requirements

Primary Android screens: 1. Onboarding and permissions 2. Home dashboard
3. Availability modes 4. Live agent/call status 5. Call history 6. Call
detail 7. Contacts 8. Memory/approved facts 9. Pending actions/approvals
10. Notifications 11. Voice/language settings 12. Privacy and data
controls 13. Account/security settings

Home screen must display: - Current mode and server sync state - ZORO
service status - Recent handled calls - Pending actions - Urgent
notifications - Quick mode switch

Call detail must display: - Caller and number - Start/end/duration -
Mode at time of call - AI disclosure/consent status - Summary and
intent - Transcript if available - Action items - Escalation status -
Recording availability only where permitted - Relevant audit events

## 11. Non-functional requirements

  -----------------------------------------------------------------------
  Area                                Requirement
  ----------------------------------- -----------------------------------
  Reliability                         Cloud call handling independent of
                                      Android app process

  Availability                        Initial backend target 99.5%,
                                      subject to hosting/provider SLA

  Latency                             Target low-latency turn-taking;
                                      measure end-of-utterance to first
                                      audio

  Security                            TLS, encrypted storage, least
                                      privilege

  Privacy                             Consent, retention, export and
                                      deletion

  Observability                       Correlation IDs, structured logs,
                                      metrics

  Scalability                         Isolated sessions; bounded
                                      concurrent calls

  Accessibility                       Android accessibility and readable
                                      UI

  Offline                             Cached call history/settings; clear
                                      stale mode state

  Maintainability                     Modular adapters and automated
                                      tests
  -----------------------------------------------------------------------

## 12. Acceptance criteria for v1

A release candidate passes only when: 1. A real inbound call reaches
configured ZORO number. 2. ZORO identifies itself as AI assistant. 3.
Caller can conduct a natural conversation. 4. AI answers only with
approved context. 5. Sensitive request is refused or escalated. 6.
Interruption and hang-up work. 7. Call record is persisted. 8.
Transcript is stored only under configured consent policy. 9. Summary
and action items are generated. 10. Android receives notification. 11.
Owner can review and manage actions. 12. Authorization and
tenant-isolation tests pass. 13. Failure paths are tested and
documented.

## 13. Risks and mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  SIM call audio inaccessible         Dedicated number/verified
                                      forwarding

  Carrier forwarding unsupported      Provider number remains initial
                                      route

  AI hallucination                    Grounded retrieval, confidence
                                      checks, fallback

  Caller impersonation                Treat caller ID as weak signal;
                                      verify sensitive requests

  Prompt injection                    Untrusted-input boundaries and
                                      server-side policy

  Recording law differences           Country-specific legal review and
                                      consent controls

  Provider outage                     Fallback message/voicemail and
                                      owner notification

  Cost spikes                         Duration limits, quotas, alerts

  Android background restrictions     FCM, server-side work, WorkManager
                                      for deferrable sync

  Data breach                         Encryption, tenant isolation,
                                      audit, least privilege
  -----------------------------------------------------------------------

## 14. Open product decisions

Do not hardcode assumptions for: - Owner's country and carrier. -
Android device model/version. - Telephony provider and region. -
Languages and voice. - Recording/transcription preference. - Data
retention period. - Emergency escalation contacts. - Dedicated number
versus carrier-forwarded number.

Use configurable settings and request owner decisions when they block
real deployment.
