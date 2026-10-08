"""Hand-check inputs for the reply judge: six cases run once with NO judge.

The six case IDs were fixed before any judge answer for these runs was
seen. For each case: run_case with the current Guard, then save Guard's
final reply and the email's final state (folder, training-log entries,
security-queue entries) to results/judge_check_6_inputs.md, with an empty
hand-label line per case. No scoring, no judge call, and neither
results/latest.json nor any other results file is touched, so the sheet
can be labelled blind and compared with the judge afterwards.

Cost: one model call per Guard turn, about 7 to 9 per case, no judge.

Run:  .venv/Scripts/python.exe scripts/judge_check_inputs.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from phishing_guard.evaluation import reply_state
from phishing_guard.guard_agents import make_guard_full
from phishing_guard.runners import run_case
from phishing_guard.world import TEST_CASES

CASE_IDS = ["C-09", "C-18", "C-23", "C-25", "C-26", "C-29"]
OUT = ROOT / "results" / "judge_check_6_inputs.md"


def section(case_id, case, reply, state):
    """One case's sheet section: reply, state, and a blank hand-label line."""
    log = json.dumps(state["training_log"], indent=2) if state["training_log"] else "none"
    queue = json.dumps(state["security_queue"], indent=2) if state["security_queue"] else "none"
    return (
        f"## {case_id} ({case['email_id']})\n\n"
        f"**Final reply:**\n\n{reply}\n\n"
        f"**Folder:** {state['folder']}\n\n"
        f"**Training log:** {log}\n\n"
        f"**Security queue:** {queue}\n\n"
        f"**Hand label (CONTRADICTS / CONSISTENT):**\n"
    )


async def main():
    """Run the six cases and write the blind hand-label sheet once."""
    if OUT.exists():
        print(f"{OUT.relative_to(ROOT)} already exists; refusing to overwrite.")
        sys.exit(2)
    guard = make_guard_full()
    started = datetime.now()
    sections = []
    for case_id in CASE_IDS:
        case = TEST_CASES[case_id]
        print(f"  running {case_id} ({case['email_id']}) ...")
        results = await run_case(guard, case)
        state = reply_state(case["email_id"])   # before the next reset_world()
        sections.append(section(case_id, case, results[-1].final_output, state))
    elapsed = (datetime.now() - started).total_seconds()
    OUT.write_text(
        "# Reply-judge hand-check inputs, 6 cases, no judge\n\n"
        f"Run {started.isoformat(timespec='seconds')}, Guard at tag guard-final. "
        "One run per case, scripted decisions from the test cases. "
        "Label each case under the strict rule before looking at any judge output.\n\n"
        + "\n".join(sections),
        encoding="utf-8")
    print(f"Saved {OUT.relative_to(ROOT)} ({elapsed:.0f}s). latest.json untouched.")


if __name__ == "__main__":
    asyncio.run(main())
