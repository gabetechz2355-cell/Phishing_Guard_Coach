"""Function tools Guard can call.

Sunday: four evidence tools and record_verdict.
Monday: move_to_phishing_folder (human approval + check_move guardrail),
log_training_event, and escalate_to_security. The Coach tool is built in
guard_agents.py because it wraps an Agent.

Design choices that make these gradeable (PLAN.md, Tool specs):
- check_sender_domain and check_url take the value itself, so Guard must
  extract the right domain or link. Argument correctness checks that.
- The verdict is a tool argument, so code reads it from the trace.
- Tools return data on failure ({"error": ...}) and never raise, so one bad
  call cannot crash a 30-case run.
"""

import json

from agents import function_tool
from agents.tool_guardrails import ToolGuardrailFunctionOutput, tool_input_guardrail

from .classifier import load_classifier, top_words
from .world import MAILBOX, SECURITY_QUEUE, THREAT_INTEL, TRAINING_LOG, USERS

clf = load_classifier()


# ---- INVESTIGATE: evidence tools -------------------------------------------

@function_tool
def classify_email_text(email_id: str) -> dict:
    """Score an email's text with the trained classifier. Returns the phishing
    probability (0 to 1) and the words that pushed the score most."""
    email = MAILBOX.get(email_id)
    if email is None:
        return {"error": "Email not found"}
    text = email["subject"] + " " + email["body"]
    prob = float(clf.predict_proba([text])[0][1])
    return {"phishing_probability": round(prob, 2), "top_words": top_words(text)}


@function_tool
def check_sender_domain(domain: str) -> dict:
    """Look up a sender's email domain: reputation, age in days, and whether
    it imitates a known domain."""
    return THREAT_INTEL["domains"].get(
        domain.lower().strip(),
        {"reputation": "unknown", "age_days": None, "lookalike_of": None})


@function_tool
def check_url(url: str) -> dict:
    """Look up one link from an email: reputation, lookalike target, and
    whether it is on the blocklist. Use only for links that appear in the email."""
    return THREAT_INTEL["urls"].get(
        url.strip(), {"reputation": "unknown", "on_blocklist": False})


@function_tool
def get_user_profile(user_id: str) -> dict:
    """Get an employee's role, the outside domains they normally deal with,
    and their past phishing misses by category."""
    return USERS.get(user_id, {"error": "User not found"})


# ---- DECIDE ----------------------------------------------------------------

@function_tool
def record_verdict(email_id: str, verdict: str, red_flags: list[str]) -> str:
    """Record the verdict for an email before taking any action.
    verdict must be 'legitimate', 'suspicious', or 'phishing'.
    red_flags lists the specific warning signs found (empty if none)."""
    if verdict not in ("legitimate", "suspicious", "phishing"):
        return "Error: verdict must be legitimate, suspicious, or phishing."
    email = MAILBOX.get(email_id)
    if email is None:
        return "Error: Email not found."
    email["verdict"] = verdict
    email["red_flags"] = red_flags
    return f"Verdict recorded for {email_id}: {verdict}."


# ---- ACT: the approval tool and its guardrail ------------------------------

@tool_input_guardrail
def check_move(data):
    """Block the move when the email ID is unknown, when no verdict is
    recorded, or when the recorded verdict is legitimate. Same pattern as the
    tutorial's check_refund. Runs after approval, right before execution, so
    approval cannot override it. It is a backstop, not a gate on the prompt."""
    arguments = json.loads(data.context.tool_arguments)
    email = MAILBOX.get(arguments.get("email_id"))
    if email is None:
        return ToolGuardrailFunctionOutput.reject_content("Blocked: unknown email ID.")
    verdict = email.get("verdict")
    if verdict is None:
        return ToolGuardrailFunctionOutput.reject_content(
            "Blocked: record_verdict must be called before any move.")
    if verdict == "legitimate":
        return ToolGuardrailFunctionOutput.reject_content(
            "Blocked: the recorded verdict is legitimate, so the email stays in the Inbox.")
    return ToolGuardrailFunctionOutput.allow()


@function_tool(needs_approval=True, tool_input_guardrails=[check_move])
def move_to_phishing_folder(email_id: str, reason: str) -> str:
    """Move an email from the Inbox to the Phishing folder. The employee
    must approve. reason is one sentence the employee will read."""
    email = MAILBOX.get(email_id)
    if email is None:
        return "Error: Email not found."
    email["folder"] = "Phishing"
    return f"{email_id} moved to the Phishing folder."


# ---- FOLLOW UP -------------------------------------------------------------

@function_tool
def log_training_event(user_id: str, email_id: str, outcome: str) -> str:
    """Log the employee's decision on a flagged email.
    outcome is 'reported' (approved the move) or 'missed' (rejected it)."""
    if outcome not in ("reported", "missed"):
        return "Error: outcome must be 'reported' or 'missed'."
    email = MAILBOX.get(email_id)
    if email is None:
        return "Error: Email not found."
    TRAINING_LOG.append({"user_id": user_id, "email_id": email_id, "outcome": outcome})
    if email.get("is_simulation"):
        return ("Logged. This email was a training simulation sent by the "
                "security team. Tell the employee.")
    return "Logged."


@function_tool
def escalate_to_security(email_id: str, summary: str) -> str:
    """Send an email to the security team's review queue with a short summary."""
    if email_id not in MAILBOX:
        return "Error: Email not found."
    SECURITY_QUEUE.append({"email_id": email_id, "summary": summary})
    return f"Escalated as SEC-{len(SECURITY_QUEUE):03d}."


# ---- tool lists ------------------------------------------------------------

EVIDENCE_TOOLS = [classify_email_text, check_sender_domain, check_url, get_user_profile]
SUNDAY_TOOLS = EVIDENCE_TOOLS + [record_verdict]
ACTION_TOOLS = [move_to_phishing_folder]
FOLLOW_UP_TOOLS = [log_training_event, escalate_to_security]
# Everything except coach_user, which guard_agents.make_guard_full inserts
# between the action tool and the follow-ups so the order matches PLAN.md.
FUNCTION_TOOLS = SUNDAY_TOOLS + ACTION_TOOLS + FOLLOW_UP_TOOLS
