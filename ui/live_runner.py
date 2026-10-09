"""Live runner: the real Guard driven through the server.

This is run_interactive's loop (phishing_guard/runners.py:33) with the
keyboard replaced by the server's decision queue. It calls only what the
tutorial and runners.py call: Runner.run, result.to_state(),
state.approve(request), state.reject(request, rejection_message=...).
The rejection message string and the default reason are copied verbatim
from runners.py so the live UI run is indistinguishable from run_interactive
and run_case to Guard. No Guard step is re-implemented and nothing in
phishing_guard/ changes.
"""

from agents import Runner

from phishing_guard.guard_agents import build_input, make_guard_full

from .events import run_with_pauses

REJECTION_PREFIX = "The employee rejected the move. Their reason: "
DEFAULT_REASON = "I think this email is fine."   # run_case's fallback


def make_live_runner(max_turns=12):
    """An async runner(email_id, log, get_decision) for ui.server.App."""
    guard = make_guard_full()

    async def runner(email_id, log, get_decision):
        """One live case: real SDK segments driven through run_with_pauses."""
        async def start_segment():
            """First segment: one Runner.run on the case's built input."""
            return await Runner.run(guard, build_input(email_id),
                                    max_turns=max_turns)

        async def resume_segment(result, decision, reason):
            """Apply the decision to every pending request, then resume."""
            state = result.to_state()
            for request in result.interruptions:
                if decision == "approve":
                    state.approve(request)
                else:
                    state.reject(request, rejection_message=(
                        REJECTION_PREFIX + (reason or DEFAULT_REASON)))
            return await Runner.run(guard, state)

        await run_with_pauses(log, email_id, start_segment, resume_segment,
                              get_decision)

    return runner
