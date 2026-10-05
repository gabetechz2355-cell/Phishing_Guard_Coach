"""Trace reading shared by the Monday demo check and Tuesday's scorer.

Monday: collect_calls and expected_follow_up, both PLAN.md verbatim, plus
collect_outputs for reading tool results (the Coach's lesson, the
simulation reveal) straight from the trace.
Tuesday adds score_case, the run loop, and the lesson judge.
"""

import json

EVIDENCE = {"classify_email_text", "check_sender_domain", "check_url", "get_user_profile"}
ID_TOOLS = {"record_verdict", "move_to_phishing_folder",
            "log_training_event", "escalate_to_security"}


def collect_calls(results):
    """Unique function calls across every result segment, in order.

    A paused run holds a tool_call_item and a tool_approval_item with the
    same call_id, and the resumed segment repeats both, so dedupe by call_id.
    """
    calls = {}
    for result in results:
        for item in result.new_items:
            if item.type in ("tool_call_item", "tool_approval_item"):
                raw = item.raw_item
                if raw.type == "function_call" and raw.call_id not in calls:
                    calls[raw.call_id] = {"name": raw.name,
                                          "args": json.loads(raw.arguments)}
    return list(calls.values())


def collect_call_ids(results):
    """call_ids in the same order collect_calls returns them."""
    ids = []
    for result in results:
        for item in result.new_items:
            if item.type in ("tool_call_item", "tool_approval_item"):
                raw = item.raw_item
                if raw.type == "function_call" and raw.call_id not in ids:
                    ids.append(raw.call_id)
    return ids


def collect_outputs(results):
    """call_id -> tool output string, across every segment."""
    outputs = {}
    for result in results:
        for item in result.new_items:
            if item.type == "tool_call_output_item":
                raw = item.raw_item
                call_id = raw["call_id"] if isinstance(raw, dict) else raw.call_id
                outputs[call_id] = item.output
    return outputs


def expected_follow_up(verdict, decision):
    """One row of the HITL table: (folder, logged outcome, coach, escalated)."""
    if verdict == "legitimate":
        return ("Inbox", None, False, False)
    if decision == "approve":
        return ("Phishing", "reported", False, verdict == "suspicious")
    return ("Inbox", "missed", True, True)
