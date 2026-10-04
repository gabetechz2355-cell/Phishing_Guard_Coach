"""Sunday end-of-day check: Guard records a sensible verdict on three emails.

Runs demo cases A (E-001), B (E-002), and C (E-003) through Guard with only
the five investigate/decide tools, prints each trace, and compares the
recorded verdict with the test case's expected verdict.

Run:  .venv\\Scripts\\python.exe scripts\\sunday_check.py [E-00x ...]
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from phishing_guard.guard_agents import SUNDAY_ADDENDUM, make_guard
from phishing_guard.runners import recorded_verdict, run_investigation
from phishing_guard.tools import SUNDAY_TOOLS
from phishing_guard.trace_utils import show_trace
from phishing_guard.world import TEST_CASES

DEFAULT = ["E-001", "E-002", "E-003"]


async def main(email_ids):
    guard = make_guard(SUNDAY_TOOLS, SUNDAY_ADDENDUM)
    expected = {c["email_id"]: c["expected_verdict"] for c in TEST_CASES.values()}
    rows = []
    for eid in email_ids:
        print("\n" + "=" * 72)
        print(f"{eid}  expected verdict: {expected.get(eid)}")
        print("=" * 72)
        result = await run_investigation(guard, eid)
        show_trace(result)
        rv = recorded_verdict(eid)
        calls = [i.raw_item.name for i in result.new_items
                 if i.type == "tool_call_item" and i.raw_item.type == "function_call"]
        print(f"\nRecorded: {rv}")
        print(f"Tool calls in order: {calls}")
        rows.append((eid, expected.get(eid), rv["verdict"], len(calls)))

    print("\n" + "=" * 72)
    print("SUMMARY")
    print(f"{'email':<7}{'expected':<13}{'recorded':<13}{'tool calls':<12}{'match'}")
    ok = 0
    for eid, exp, rec, n in rows:
        match = exp == rec
        ok += match
        print(f"{eid:<7}{str(exp):<13}{str(rec):<13}{n:<12}{'yes' if match else 'NO'}")
    print(f"\n{ok}/{len(rows)} verdicts match the expected verdict.")
    sys.exit(0 if ok == len(rows) else 1)


asyncio.run(main(sys.argv[1:] or DEFAULT))
