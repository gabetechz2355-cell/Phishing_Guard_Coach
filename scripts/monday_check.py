"""Monday end-of-day check: both demo cases produce the expected trace.

Runs demo case A (C-01, approve path) and B (C-02, reject and coaching path)
through run_case with the full nine-tool Guard, then checks the trace and
the world state against the test case and PLAN.md's HITL table. With
--repeat N each case runs N times and every run must pass.

Run:  .venv/Scripts/python.exe scripts/monday_check.py [--repeat 2] [--quiet] [C-01 C-02 ...]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from phishing_guard.evaluation import (EVIDENCE, ID_TOOLS, collect_call_ids,
                                       collect_calls, collect_outputs,
                                       expected_follow_up)
from phishing_guard.guard_agents import make_guard_full
from phishing_guard.runners import run_case
from phishing_guard.trace_utils import show_trace
from phishing_guard.world import MAILBOX, SECURITY_QUEUE, TEST_CASES, TRAINING_LOG

DEFAULT = ["C-01", "C-02"]
PUNCT = ".,;:!?()\"'*"


def _words(text):
    return [w.strip(PUNCT).lower() for w in text.split() if w.strip(PUNCT)]


def _overlap(lesson, reply):
    """Share of the lesson's words that appear in the reply: a loose check
    that Guard passed the lesson through rather than paraphrasing it."""
    lw = _words(lesson)
    rw = set(_words(reply))
    return sum(w in rw for w in lw) / max(len(lw), 1)


def check_trace(case, results):
    """Return an ordered dict of check -> (passed, detail). Reads the world
    state, so call it right after run_case and before the next reset."""
    calls = collect_calls(results)
    call_ids = collect_call_ids(results)
    outputs = collect_outputs(results)
    names = [c["name"] for c in calls]
    eid = case["email_id"]
    email = MAILBOX[eid]
    verdict = email.get("verdict")
    decision = case["user_decision"]
    checks = {}

    checks["verdict matches expected"] = (
        verdict == case["expected_verdict"], f"recorded={verdict}")
    checks["record_verdict called once"] = (
        names.count("record_verdict") == 1, f"count={names.count('record_verdict')}")
    checks["required tools called"] = (
        set(case["required_tools"]) <= set(names),
        f"missing={sorted(set(case['required_tools']) - set(names))}")
    checks["no forbidden tools"] = (
        not set(names) & set(case["forbidden_tools"]),
        f"used={sorted(set(names) & set(case['forbidden_tools']))}")

    i_verdict = names.index("record_verdict") if "record_verdict" in names else -1
    i_move = (names.index("move_to_phishing_folder")
              if "move_to_phishing_folder" in names else len(names))
    i_evidence = [i for i, n in enumerate(names) if n in EVIDENCE]
    checks["order: evidence, verdict, move"] = (
        bool(i_evidence) and max(i_evidence) < i_verdict < i_move, " > ".join(names))

    flagged = case["expected_verdict"] in ("suspicious", "phishing")
    checks["move requested iff flagged"] = (
        ("move_to_phishing_folder" in names) == flagged,
        f"move called={'move_to_phishing_folder' in names}, expected={flagged}")
    checks["one pause, then resumed"] = (
        len(results) == (2 if flagged else 1) and not results[-1].interruptions,
        f"segments={len(results)}, pending={len(results[-1].interruptions)}")

    logged = [r["outcome"] for r in TRAINING_LOG if r["email_id"] == eid]
    state = (email["folder"], logged[-1] if logged else None,
             "coach_user" in names,
             any(q["email_id"] == eid for q in SECURITY_QUEUE))
    want = expected_follow_up(case["expected_verdict"], decision)
    checks["follow-up matches HITL table"] = (
        state == want, f"(folder, logged, coach, escalated) got={state} want={want}")

    domain = email["from_addr"].split("@")[-1].lower()
    bad_args = [c for c in calls if not (
        (c["name"] != "check_sender_domain"
         or c["args"].get("domain", "").lower().strip() == domain)
        and (c["name"] != "check_url"
             or c["args"].get("url", "").strip() in email["links"])
        and (c["name"] not in ID_TOOLS or c["args"].get("email_id") == eid))]
    checks["arguments correct"] = (not bad_args, f"bad={bad_args}")

    seen = [(c["name"], json.dumps(c["args"], sort_keys=True)) for c in calls]
    checks["no duplicate calls"] = (len(seen) == len(set(seen)), f"calls={len(seen)}")

    final = results[-1].final_output or ""
    if decision == "reject" and flagged:
        lesson = next((outputs.get(cid) for cid, c in zip(call_ids, calls)
                       if c["name"] == "coach_user"), None)
        words = len(_words(lesson)) if lesson else 0
        checks["lesson 120 words or fewer"] = (0 < words <= 120, f"words={words}")
        ov = _overlap(lesson, final) if lesson else 0.0
        checks["lesson appears in reply"] = (
            bool(lesson) and ov >= 0.8, f"word overlap={ov:.2f}")
    if email.get("is_simulation") and flagged:
        checks["reply reveals the simulation"] = (
            "simulation" in final.lower(), "'simulation' in final_output")
    return checks


async def main(case_ids, repeat, quiet):
    guard = make_guard_full()
    rows = []
    for case_id in case_ids:
        case = TEST_CASES[case_id]
        for n in range(1, repeat + 1):
            print("\n" + "=" * 72)
            print(f"{case_id} run {n}/{repeat}  email {case['email_id']}  "
                  f"expected {case['expected_verdict']}  decision {case['user_decision']}")
            print("=" * 72)
            results = await run_case(guard, case)
            if not quiet:
                for i, r in enumerate(results):
                    print(f"\n--- segment {i} ({len(r.new_items)} items) ---")
                    show_trace(r)
            print("\nFINAL OUTPUT:\n" + (results[-1].final_output or "<none>"))
            checks = check_trace(case, results)
            print()
            for label, (ok, detail) in checks.items():
                print(f"  [{'ok ' if ok else 'FAIL'}] {label}: {detail}")
            rows.append((case_id, n, all(ok for ok, _ in checks.values()),
                         len(collect_calls(results))))

    print("\n" + "=" * 72 + "\nSUMMARY")
    for case_id, n, ok, ncalls in rows:
        print(f"  {case_id} run {n}: {'PASS' if ok else 'FAIL'}  ({ncalls} tool calls)")
    passed = sum(ok for _, _, ok, _ in rows)
    print(f"\n{passed}/{len(rows)} runs produced the expected trace.")
    sys.exit(0 if passed == len(rows) else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="*", default=DEFAULT)
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--quiet", action="store_true", help="skip show_trace output")
    a = ap.parse_args()
    asyncio.run(main(a.cases, a.repeat, a.quiet))
