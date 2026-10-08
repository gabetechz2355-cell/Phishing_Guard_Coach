"""Sunday checklist item: verify SDK pause, resume, and what new_items holds
after a resume. Uses a throwaway agent with one needs_approval tool, so it
costs a handful of small model calls. Independent of the phishing world.

Run:  .venv\\Scripts\\python.exe scripts\\probe_sdk.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents import Agent, Runner, function_tool

from phishing_guard.config import has_openai_key, lm_model

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)


@function_tool(needs_approval=True)
def confirm_action(action: str) -> str:
    """Perform a named action. A human must approve first."""
    return f"Action '{action}' performed."


probe = Agent(
    name="Probe",
    instructions=(
        "Call confirm_action exactly once with action='probe'. "
        "If it succeeds, reply 'done'. If it is rejected, do not retry; reply 'declined'."
    ),
    model=lm_model,
    tools=[confirm_action],
)


def dump(label, result):
    """Print every new_item, pending interruption, and the final output."""
    print(f"\n--- {label}: {len(result.new_items)} new_items, "
          f"{len(result.interruptions)} interruptions ---")
    for i, item in enumerate(result.new_items):
        raw = item.raw_item
        call_id = getattr(raw, "call_id", None) or getattr(item, "call_id", None)
        name = getattr(raw, "name", None)
        extra = ""
        if item.type == "tool_call_output_item":
            extra = f" output={item.output!r}"
        print(f"  [{i}] {item.type:<24} raw={type(raw).__name__ if not isinstance(raw, dict) else 'dict'}"
              f" name={name} call_id={call_id}{extra}")
    for r in result.interruptions:
        print(f"  pending: tool={r.tool_name} args={r.arguments} call_id={r.raw_item.call_id}")
    print(f"  final_output={result.final_output!r}")


async def main():
    """Pause-resume both ways, then answer the plan's call_id question."""
    print("== Run 1: approve path ==")
    r1 = await Runner.run(probe, "Please perform the probe action.", max_turns=6)
    dump("before resume", r1)
    assert r1.interruptions, "expected a pause for approval"
    state = r1.to_state()
    for req in r1.interruptions:
        state.approve(req)
    r2 = await Runner.run(probe, state)
    dump("after resume (approved)", r2)

    print("\n== Run 2: reject path ==")
    r3 = await Runner.run(probe, "Please perform the probe action.", max_turns=6)
    dump("before resume", r3)
    assert r3.interruptions, "expected a pause for approval"
    state = r3.to_state()
    for req in r3.interruptions:
        state.reject(req, rejection_message="The human declined. Do not retry.")
    r4 = await Runner.run(probe, state)
    dump("after resume (rejected)", r4)

    # The question the plan asks: do pre-pause items repeat after a resume?
    ids_before = {getattr(i.raw_item, "call_id", None) for i in r1.new_items}
    ids_after = {getattr(i.raw_item, "call_id", None) for i in r2.new_items}
    print("\n== Summary ==")
    print("call_ids before resume:", ids_before - {None})
    print("call_ids after resume: ", ids_after - {None})
    print("repeat of pre-pause call_ids after resume:",
          bool((ids_before - {None}) & (ids_after - {None})))


asyncio.run(main())
