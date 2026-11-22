from dataclasses import dataclass
import re


AI_DISCLOSURE = (
    "Hello, I’m ZORO, an AI assistant. I’m answering in a text simulation. "
    "I can take a message for the owner, but I can’t make commitments or share private information."
)

_SENSITIVE = re.compile(
    r"\b(password|passcode|otp|one[- ]time code|bank account|bank balance|"
    r"credit card|medical|diagnos(?:is|es)|medication|home address|exact location|"
    r"where (?:is|are|does) (?:he|she|they|the owner)|live location|private (?:number|email))\b",
    re.IGNORECASE,
)
_COMMITMENT = re.compile(
    r"\b(accept (?:the )?(?:offer|contract|deal)|sign (?:the )?(?:contract|agreement)|"
    r"promise|commit(?:ment)?|agree on (?:their|the owner's) behalf|pay(?:ment)?|"
    r"transfer (?:the )?money|book (?:the )?(?:flight|hotel|ticket))\b",
    re.IGNORECASE,
)
_AVAILABILITY = re.compile(
    r"\b(is|are) (?:the owner|he|she|they) (?:available|free|busy)|"
    r"when (?:will|can) (?:the owner|he|she|they) (?:be )?(?:free|available)\b",
    re.IGNORECASE,
)
_URGENT = re.compile(
    r"\b(emergency|urgent|urgently|accident|hurt|injured|danger|ambulance|hospital|"
    r"can't breathe|cannot breathe|fire|threat)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ResponseCandidate:
    intent: str
    proposed_response: str
    proposed_action: str
    urgency: str = "normal"


def propose_response(caller_text: str) -> ResponseCandidate:
    if _URGENT.search(caller_text):
        return ResponseCandidate(
            intent="urgent_message",
            proposed_response=(
                "This sounds urgent. This simulation can save your message, but it cannot "
                "contact emergency services or alert anyone automatically. If someone is in "
                "immediate danger, contact local emergency services now."
            ),
            proposed_action="record_message",
            urgency="urgent",
        )
    if _SENSITIVE.search(caller_text):
        return ResponseCandidate(
            intent="private_information_request",
            proposed_response=(
                "I can’t share private information. I can record your request for the owner."
            ),
            proposed_action="record_message",
        )
    if _COMMITMENT.search(caller_text):
        return ResponseCandidate(
            intent="commitment_request",
            proposed_response=(
                "I can’t make agreements, payments, bookings, or other commitments for the owner. "
                "I can record your request for their review."
            ),
            proposed_action="record_message",
        )
    if _AVAILABILITY.search(caller_text):
        return ResponseCandidate(
            intent="availability_request",
            proposed_response=(
                "I can’t confirm the owner’s availability. I can take a message and ask them to get back to you."
            ),
            proposed_action="record_message",
        )
    return ResponseCandidate(
        intent="message_or_general",
        proposed_response="I can take a message for the owner. What would you like me to pass along?",
        proposed_action="record_message",
    )


def evaluate_candidate(candidate: ResponseCandidate) -> dict[str, object]:
    """Deterministic guardrail: only storing the caller's message is an available action."""
    action_allowed = candidate.proposed_action == "record_message"
    return {
        "decision": "allow" if action_allowed else "deny",
        "intent": candidate.intent,
        "urgency": candidate.urgency,
        "proposed_action": candidate.proposed_action,
        "allowed_actions": ["record_message"],
        "action_allowed": action_allowed,
        "reason": "The simulation has no external-action tools; caller messages can be recorded for owner review."
        if action_allowed
        else "Action is outside the simulation allowlist.",
    }
