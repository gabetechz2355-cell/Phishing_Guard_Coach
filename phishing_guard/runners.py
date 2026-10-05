"""Runners.

Sunday: run_investigation, a single run with no approval pause.
Monday: run_interactive (a person types approve or reject) and run_case (the
decision comes from the test case). Both are PLAN.md's Human-in-the-loop
code. Both stop after three pauses in case Guard keeps retrying, and both
return every result segment so the scorers can read new_items from all of
them and drop repeats by call_id (the SDK repeats pre-pause items after a
resume; see scripts/probe_sdk.py).
"""

import json

from agents import Runner

from .guard_agents import build_input
from .world import MAILBOX, reset_world

MAX_PAUSES = 3


async def run_investigation(guard, email_id: str, max_turns: int = 12):
    """Reset the world, run Guard on one email once, return the result.

    Sunday's end-of-day check: Guard should call the evidence tools, then
    record_verdict, then reply. The recorded verdict is read from MAILBOX.
    """
    reset_world()
    result = await Runner.run(guard, build_input(email_id), max_turns=max_turns)
    return result


async def run_interactive(guard, email_id: str, max_turns: int = 12):
    """Live demo: a person types approve or reject."""
    reset_world()
    result = await Runner.run(guard, build_input(email_id), max_turns=max_turns)
    results = [result]
    for _ in range(MAX_PAUSES):
        if not result.interruptions:
            break
        state = result.to_state()
        for request in result.interruptions:
            args = json.loads(request.arguments)
            print(f"\nGuard wants to move {args['email_id']} to Phishing.")
            print("Reason:", args["reason"])
            decision = ""
            while decision not in ("approve", "reject"):
                decision = input("Approve or reject? ").strip().lower()
            if decision == "approve":
                state.approve(request)
            else:
                why = input("Why do you trust this email? ").strip()
                state.reject(request, rejection_message=(
                    "The employee rejected the move. Their reason: " + why))
        result = await Runner.run(guard, state)
        results.append(result)
    print(result.final_output)
    return results


async def run_case(guard, case: dict, max_turns: int = 12):
    """Evaluation: the decision comes from the test case."""
    reset_world()
    result = await Runner.run(guard, build_input(case["email_id"]), max_turns=max_turns)
    results = [result]
    for _ in range(MAX_PAUSES):
        if not result.interruptions:
            break
        state = result.to_state()
        for request in result.interruptions:
            if case["user_decision"] == "approve":
                state.approve(request)
            else:
                reason = case["user_reason"] or "I think this email is fine."
                state.reject(request, rejection_message=(
                    "The employee rejected the move. Their reason: " + reason))
        result = await Runner.run(guard, state)
        results.append(result)
    return results


def recorded_verdict(email_id: str) -> dict:
    """What record_verdict wrote for this email in the current world state."""
    e = MAILBOX[email_id]
    return {"verdict": e.get("verdict"), "red_flags": e.get("red_flags")}
