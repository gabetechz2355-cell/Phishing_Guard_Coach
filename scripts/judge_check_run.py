"""Judge the six saved hand-check replies. Guard is NOT run.

Reads results/judge_check_6_inputs.md (replies, final states, and the hand
labels), rebuilds each case's state dict, and asks the reply judge once per
case through the same build_judge_input / parse path the harness uses. The
judge and the scorer are not edited. Prints each judge answer and reason
with the hand label beside it; writes no results file and never touches
results/latest.json.

Cost: one judge call per case, six in all.

Run:  .venv/Scripts/python.exe scripts/judge_check_run.py
"""

import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from agents import Runner

from phishing_guard.evaluation import judge_result
from phishing_guard.judge import build_judge_input, make_judge

INPUTS = ROOT / "results" / "judge_check_6_inputs.md"

SECTION = re.compile(
    r"^## (C-\d+) \((E-\d+)\)\n\n"
    r"\*\*Final reply:\*\*\n\n(.*?)\n\n"
    r"\*\*Folder:\*\* (.+?)\n\n"
    r"\*\*Training log:\*\* (.*?)\n\n"
    r"\*\*Security queue:\*\* (.*?)\n\n"
    r"\*\*Hand label \(CONTRADICTS / CONSISTENT\):[\s*]*(\w*)[\s*]*$",
    re.DOTALL | re.MULTILINE)


def parse_sheet(text):
    blocks = re.split(r"(?=^## C-)", text, flags=re.MULTILINE)[1:]
    cases = []
    for block in blocks:
        m = SECTION.match(block.strip() + "\n")
        if not m:
            cid = block.split()[1] if len(block.split()) > 1 else "?"
            print(f"Could not parse the section for {cid}; fix the sheet and rerun.")
            sys.exit(2)
        cid, eid, reply, folder, log, queue, label = m.groups()
        cases.append({
            "case_id": cid,
            "state": {"email_id": eid, "folder": folder.strip(),
                      "training_log": [] if log.strip() == "none" else json.loads(log),
                      "security_queue": [] if queue.strip() == "none" else json.loads(queue)},
            "reply": reply.strip(),
            "hand_label": label.strip().upper() or None,
        })
    return cases


async def main():
    cases = parse_sheet(INPUTS.read_text(encoding="utf-8"))
    print(f"Judging {len(cases)} saved replies (Guard not run).")
    judge = make_judge()
    for c in cases:
        result = await Runner.run(
            judge, build_judge_input(c["state"], c["reply"]), max_turns=2)
        row = judge_result(result.final_output, state=c["state"])
        answer = (row["judge_answer"] or "unparseable").upper()
        agree = ("n/a" if c["hand_label"] is None
                 else "AGREE" if answer == c["hand_label"] else "DISAGREE")
        print(f"\n{c['case_id']}  judge: {answer}  hand: {c['hand_label']}  -> {agree}")
        print("  " + " ".join((row["judge_reason"] or row["judge_error"] or "").split()))


if __name__ == "__main__":
    asyncio.run(main())
