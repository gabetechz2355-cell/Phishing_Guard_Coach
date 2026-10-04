"""Function tools Guard can call. Sunday: four evidence tools and record_verdict.

Design choices that make these gradeable (PLAN.md, Tool specs):
- check_sender_domain and check_url take the value itself, so Guard must
  extract the right domain or link. Argument correctness checks that.
- The verdict is a tool argument, so code reads it from the trace.
- Tools return data on failure ({"error": ...}) and never raise, so one bad
  call cannot crash a 30-case run.

Monday adds move_to_phishing_folder (approval + guardrail), log_training_event,
and escalate_to_security.
"""

from agents import function_tool

from .classifier import load_classifier, top_words
from .world import MAILBOX, THREAT_INTEL, USERS

clf = load_classifier()


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


EVIDENCE_TOOLS = [classify_email_text, check_sender_domain, check_url, get_user_profile]
SUNDAY_TOOLS = EVIDENCE_TOOLS + [record_verdict]
