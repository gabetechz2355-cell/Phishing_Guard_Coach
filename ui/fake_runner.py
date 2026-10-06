"""A fake runner for offline checks: no model, no API key, no SDK.

Builds result segments as SimpleNamespace objects shaped exactly like the
SDK's (the scripts/test_score_offline.py pattern), including the SDK's
quirk that a resumed segment repeats every pre-pause item with the same
call_id (scripts/probe_sdk.py, finding b) - so the dedupe in
ui/events.py is exercised, not bypassed. It mutates the world the way the
real tools in phishing_guard/tools.py do, so the truth strip shows real
state transitions. Tool output strings match tools.py's return values.

Scenarios:
    E-001  demo case A: phishing, pause; approve and reject both work.
    E-002  demo case B: phishing, no links, simulation; the canned reply
           repeats the real Guard habit of claiming a move after a reject,
           so the page can be checked against plan rule 5.
    E-003  demo case C: legitimate, no pause.
    E-010  odd run (plan rule 6): an unknown tool name, a suspicious
           verdict, and an early stop with no move and no follow-up.
    fail=True: the first segment raises, for the error-banner path.
"""

import asyncio
import json
from types import SimpleNamespace

from phishing_guard.world import MAILBOX, SECURITY_QUEUE, TRAINING_LOG

from .events import run_with_pauses

REJECTION_PREFIX = "The employee rejected the move. Their reason: "

LESSON_E002 = (
    "1) Red flags: the sender domain is a lookalike, billing@apex-supp1y.example; "
    "the reply-to differs from the sender; and it asks you to switch October "
    "invoice payments to a new bank account and confirm by reply.\n"
    "2) \"We pay them every month\" is a common trap: familiar vendors and "
    "routine invoices can make a fake request feel normal, so habit can "
    "override checking details.\n"
    "3) Rule for Accounts Payable: any bank-detail change must be verified "
    "through a known, already-on-file contact, not by replying to the email.")

LESSON_GENERIC = (
    "1) Red flags: the sender domain is malicious and the link is on the "
    "blocklist.\n2) Urgent password warnings are a common trap: fear of losing "
    "access pushes people to click first.\n3) Rule: open Microsoft 365 from "
    "your bookmarks, never from an email link.")

SCENARIOS = {
    "E-001": {
        "verdict": "phishing",
        "flags": ["malicious sender domain", "blocklisted malicious link",
                  "urgent password-expiration lure"],
        "user_id": "U-03",
        "evidence": [
            ("classify_email_text", {"email_id": "E-001"},
             json.dumps({"phishing_probability": 0.93,
                         "top_words": ["account", "hours", "secure", "verify"]})),
            ("check_sender_domain", {"domain": "m365-secure-login.example"},
             json.dumps({"reputation": "malicious", "age_days": 12,
                         "lookalike_of": None})),
            ("check_url", {"url": "https://m365-secure-login.example/reset?u=priya.shah"},
             json.dumps({"reputation": "malicious", "on_blocklist": True})),
            ("get_user_profile", {"user_id": "U-03"},
             json.dumps({"user_id": "U-03", "name": "Priya Shah",
                         "role": "Regional Sales", "past_misses": {}})),
        ],
        "move_reason": ("This email uses a malicious sender domain and a "
                        "blocklisted link to impersonate Microsoft 365 and "
                        "push an urgent password reset."),
        "lesson": LESSON_GENERIC,
        "reply_approve": ("Verdict: phishing. Top red flags: malicious sender "
                          "domain, blocklisted malicious link, urgent "
                          "password-expiration lure. The email was moved to "
                          "the Phishing folder and the report was logged."),
        "reply_reject": ("Verdict: phishing. Top red flags: malicious sender "
                         "domain, blocklisted malicious link. The email stays "
                         "in your Inbox at your request.\n\n" + LESSON_GENERIC),
    },
    "E-002": {
        "verdict": "phishing",
        "flags": ["lookalike sender domain", "reply-to mismatch",
                  "request to change bank details and confirm by reply"],
        "user_id": "U-01",
        "evidence": [
            ("classify_email_text", {"email_id": "E-002"},
             json.dumps({"phishing_probability": 0.75,
                         "top_words": ["account", "bank", "payment", "reply"]})),
            ("check_sender_domain", {"domain": "apex-supp1y.example"},
             json.dumps({"reputation": "suspicious", "age_days": 6,
                         "lookalike_of": "apexsupply.example"})),
            ("get_user_profile", {"user_id": "U-01"},
             json.dumps({"user_id": "U-01", "name": "Dana Ruiz",
                         "role": "Accounts Payable",
                         "known_domains": ["apexsupply.example",
                                           "coastalfreight.example"],
                         "past_misses": {"invoice_fraud": 1}})),
        ],
        "move_reason": ("The sender domain is a lookalike, the reply-to is "
                        "different, and the email requests a bank change and "
                        "reply confirmation."),
        "lesson": LESSON_E002,
        "reply_approve": ("Verdict: phishing. Top red flags: lookalike sender "
                          "domain, reply-to mismatch, bank-detail change "
                          "request. The email was moved to the Phishing "
                          "folder and the report was logged. This email was a "
                          "training simulation sent by the security team."),
        # Deliberately repeats the frozen Guard's habit: it claims the move
        # happened after a reject. The page must show it as written next to a
        # truth strip that says Inbox (plan rule 5).
        "reply_reject": ("Verdict: phishing. Top red flags: lookalike sender "
                         "domain, reply-to mismatch, bank-detail change "
                         "request. I have moved the email to the Phishing "
                         "folder.\n\n" + LESSON_E002 + "\n\nThis email was a "
                         "training simulation sent by the security team."),
    },
    "E-003": {
        "verdict": "legitimate",
        "flags": [],
        "user_id": "U-01",
        "evidence": [
            ("classify_email_text", {"email_id": "E-003"},
             json.dumps({"phishing_probability": 0.04,
                         "top_words": ["invoice", "deliveries", "september"]})),
            ("check_sender_domain", {"domain": "apexsupply.example"},
             json.dumps({"reputation": "clean", "age_days": 4100,
                         "lookalike_of": None})),
            ("check_url", {"url": "https://portal.apexsupply.example/invoices/20471"},
             json.dumps({"reputation": "clean", "on_blocklist": False})),
            ("get_user_profile", {"user_id": "U-01"},
             json.dumps({"user_id": "U-01", "name": "Dana Ruiz",
                         "role": "Accounts Payable",
                         "known_domains": ["apexsupply.example",
                                           "coastalfreight.example"]})),
        ],
        "reply_done": ("Verdict: legitimate. The sender domain and link are "
                       "clean and the invoice matches a known vendor for "
                       "Dana's Accounts Payable role. No action was taken."),
    },
    "E-010": {
        "verdict": "suspicious",
        "flags": ["unverifiable payment request"],
        "user_id": "U-01",
        "evidence": [
            ("classify_email_text", {"email_id": "E-010"},
             json.dumps({"phishing_probability": 0.55, "top_words": ["payment"]})),
            # An unknown tool name: the page must render it generically.
            ("lookup_dns_history", {"domain": "unknown-vendor.example"},
             json.dumps({"error": "no such tool in the real system"})),
        ],
        # Early stop: verdict recorded, then no move, no follow-up, reply.
        "reply_done": ("Verdict: suspicious. I could not confirm the sender "
                       "either way. Stopping here."),
    },
}


def _call(n, name, args, kind="tool_call_item"):
    return SimpleNamespace(type=kind, raw_item=SimpleNamespace(
        type="function_call", call_id=f"call_{n}", name=name,
        arguments=json.dumps(args)))


def _output(n, text):
    return SimpleNamespace(type="tool_call_output_item",
                           raw_item={"call_id": f"call_{n}"}, output=text)


def _message(text):
    return SimpleNamespace(type="message_output_item", raw_item=None,
                           output=text)


def make_fake_runner(delay=0.0, fail=False):
    """An async runner(email_id, log, get_decision) the server can drive.

    delay is seconds per fake step, so the page's investigating phase is
    visible in a browser; the offline checks use 0.
    """

    async def runner(email_id, log, get_decision):
        sc = SCENARIOS.get(email_id)
        if sc is None:
            raise ValueError(f"No fake scenario for {email_id}. "
                             f"Known: {sorted(SCENARIOS)}")

        n = iter(range(1, 50))
        items = []          # grows across segments: resumes repeat old items
        move_n = None

        async def start_segment():
            if fail:
                await asyncio.sleep(delay)
                raise RuntimeError("fake API failure: connection refused "
                                   "(set by make_fake_runner(fail=True))")
            nonlocal move_n
            await asyncio.sleep(delay * (len(sc["evidence"]) + 2))
            for name, args, out in sc["evidence"]:
                k = next(n)
                items.append(_call(k, name, args))
                items.append(_output(k, out))
            k = next(n)
            items.append(_call(k, "record_verdict",
                               {"email_id": email_id, "verdict": sc["verdict"],
                                "red_flags": sc["flags"]}))
            # The real tool writes the verdict into the mailbox.
            MAILBOX[email_id]["verdict"] = sc["verdict"]
            MAILBOX[email_id]["red_flags"] = sc["flags"]
            items.append(_output(
                k, f"Verdict recorded for {email_id}: {sc['verdict']}."))

            if sc["verdict"] == "legitimate" or "move_reason" not in sc:
                return SimpleNamespace(new_items=list(items),
                                       final_output=sc["reply_done"],
                                       interruptions=[])
            move_n = next(n)
            move_args = {"email_id": email_id, "reason": sc["move_reason"]}
            items.append(_call(move_n, "move_to_phishing_folder", move_args))
            items.append(_call(move_n, "move_to_phishing_folder", move_args,
                               kind="tool_approval_item"))
            request = SimpleNamespace(
                arguments=json.dumps(move_args),
                raw_item=SimpleNamespace(call_id=f"call_{move_n}"))
            return SimpleNamespace(new_items=list(items), final_output=None,
                                   interruptions=[request])

        async def resume_segment(result, decision, reason):
            await asyncio.sleep(delay * 3)
            simulation = bool(MAILBOX[email_id].get("is_simulation"))
            log_suffix = (" This email was a training simulation sent by the "
                          "security team. Tell the employee." if simulation else "")
            # The SDK repeats every pre-pause item on resume; so does this.
            new = list(items)
            if decision == "approve":
                MAILBOX[email_id]["folder"] = "Phishing"
                new.append(_output(
                    move_n, f"{email_id} moved to the Phishing folder."))
                k = next(n)
                new.append(_call(k, "log_training_event",
                                 {"user_id": sc["user_id"],
                                  "email_id": email_id, "outcome": "reported"}))
                TRAINING_LOG.append({"user_id": sc["user_id"],
                                     "email_id": email_id,
                                     "outcome": "reported"})
                new.append(_output(k, "Logged." + log_suffix))
                final = sc["reply_approve"]
            else:
                new.append(_output(move_n, REJECTION_PREFIX + (reason or "")))
                k = next(n)
                new.append(_call(k, "coach_user", {"input": (
                    "Email summary, red flags, the employee's reason, their "
                    "role, and the verdict.")}))
                new.append(_output(k, sc["lesson"]))
                k = next(n)
                new.append(_call(k, "log_training_event",
                                 {"user_id": sc["user_id"],
                                  "email_id": email_id, "outcome": "missed"}))
                TRAINING_LOG.append({"user_id": sc["user_id"],
                                     "email_id": email_id, "outcome": "missed"})
                new.append(_output(k, "Logged." + log_suffix))
                k = next(n)
                new.append(_call(k, "escalate_to_security",
                                 {"email_id": email_id,
                                  "summary": "Employee rejected a phishing "
                                             "warning; needs review."}))
                SECURITY_QUEUE.append({"email_id": email_id,
                                       "summary": "Employee rejected a "
                                                  "phishing warning; needs "
                                                  "review."})
                new.append(_output(
                    k, f"Escalated as SEC-{len(SECURITY_QUEUE):03d}."))
                final = sc["reply_reject"]
            new.append(_message(final))
            return SimpleNamespace(new_items=new, final_output=final,
                                   interruptions=[])

        await run_with_pauses(log, email_id, start_segment, resume_segment,
                              get_decision)

    return runner
