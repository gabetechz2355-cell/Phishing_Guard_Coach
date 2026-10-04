"""Runners. Sunday: a single investigation run with no approval pause.

Monday adds run_interactive (a person types approve or reject) and run_case
(the decision comes from the test case), both from PLAN.md.
"""

from agents import Runner

from .guard_agents import build_input
from .world import MAILBOX, reset_world


async def run_investigation(guard, email_id: str, max_turns: int = 12):
    """Reset the world, run Guard on one email, return the result.

    Sunday's end-of-day check: Guard should call the evidence tools, then
    record_verdict, then reply. The recorded verdict is read from MAILBOX.
    """
    reset_world()
    result = await Runner.run(guard, build_input(email_id), max_turns=max_turns)
    return result


def recorded_verdict(email_id: str) -> dict:
    """What record_verdict wrote for this email in the current world state."""
    e = MAILBOX[email_id]
    return {"verdict": e.get("verdict"), "red_flags": e.get("red_flags")}
