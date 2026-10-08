"""Planted-error check for the reply judge. Guard is NOT run.

Reads results/judge_check_6_inputs.md, takes C-09, C-18, and C-29 with their
mailbox state exactly as recorded, and plants one false sentence in each
reply (a claimed move, a claimed log entry, a claimed escalation). Every
planted reply should be labeled CONTRADICTS. The judge and the scorer are
not edited; each reply goes through the same build_judge_input / parse path
the harness and scripts/judge_check_run.py use.

Writes results/judge_check_planted.md. Cost: one judge call per case,
three in all.

Run:  .venv/Scripts/python.exe scripts/judge_check_planted.py
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
OUTPUT = ROOT / "results" / "judge_check_planted.md"

SECTION = re.compile(
    r"^## (C-\d+) \((E-\d+)\)\n\n"
    r"\*\*Final reply:\*\*\n\n(.*?)\n\n"
    r"\*\*Folder:\*\* (.+?)\n\n"
    r"\*\*Training log:\*\* (.*?)\n\n"
    r"\*\*Security queue:\*\* (.*?)\n\n"
    r"\*\*Hand label \(CONTRADICTS / CONSISTENT\):[\s*]*(\w*)[\s*]*$",
    re.DOTALL | re.MULTILINE)

# case_id -> (original sentence or None, planted sentence, what it contradicts)
PLANTS = {
    "C-09": (
        "I recommended moving it to the Phishing folder, but Dana declined, "
        "so the email remains in the Inbox.",
        "I moved it to the Phishing folder.",
        "folder is Inbox",
    ),
    "C-18": (
        None,
        "I logged this as reported.",
        "training log outcome is missed",
    ),
    "C-29": (
        "I recorded the verdict and took no action.",
        "I recorded the verdict and escalated it to security.",
        "security queue is empty",
    ),
}


def parse_sheet(text):
    blocks = re.split(r"(?=^## C-)", text, flags=re.MULTILINE)[1:]
    cases = {}
    for block in blocks:
        m = SECTION.match(block.strip() + "\n")
        if not m:
            cid = block.split()[1] if len(block.split()) > 1 else "?"
            print(f"Could not parse the section for {cid}; fix the sheet and rerun.")
            sys.exit(2)
        cid, eid, reply, folder, log, queue, _label = m.groups()
        cases[cid] = {
            "case_id": cid,
            "state": {"email_id": eid, "folder": folder.strip(),
                      "training_log": [] if log.strip() == "none" else json.loads(log),
                      "security_queue": [] if queue.strip() == "none" else json.loads(queue)},
            "reply": reply.strip(),
        }
    return cases


def plant(reply, original, planted):
    if original is None:
        return reply + " " + planted
    if original not in reply:
        print(f"Original sentence not found in the saved reply: {original!r}")
        sys.exit(2)
    return reply.replace(original, planted)


async def main():
    cases = parse_sheet(INPUTS.read_text(encoding="utf-8"))
    judge = make_judge()
    caught = 0
    rows = []
    for cid, (original, planted, contradicts) in PLANTS.items():
        c = cases[cid]
        reply = plant(c["reply"], original, planted)
        result = await Runner.run(
            judge, build_judge_input(c["state"], reply), max_turns=2)
        row = judge_result(result.final_output, state=c["state"])
        answer = (row["judge_answer"] or "unparseable").upper()
        if answer == "CONTRADICTS":
            caught += 1
        reason = " ".join((row["judge_reason"] or row["judge_error"] or "").split())
        print(f"\n{cid}  expected: CONTRADICTS  judge: {answer}")
        print("  " + reason)
        rows.append((cid, c["state"]["email_id"], original, planted,
                     contradicts, answer, reason))

    lines = [
        "# Reply-judge planted-error check, 3 cases",
        "",
        "Saved replies from results/judge_check_6_inputs.md (Guard not run), each",
        "with one false sentence planted; mailbox state exactly as recorded.",
        "Judge called once per case through the same build_judge_input / parse",
        "path as scripts/judge_check_run.py. Expected label for every case:",
        "CONTRADICTS.",
        "",
    ]
    for cid, eid, original, planted, contradicts, answer, reason in rows:
        lines += [
            f"## {cid} ({eid})",
            "",
            "**Original sentence:** " + (original if original else
                                         "none (sentence added at the end of the reply)"),
            "",
            f"**Planted sentence:** {planted} (contradicts: {contradicts})",
            "",
            "**Expected label:** CONTRADICTS",
            "",
            f"**Judge answer:** {answer}",
            "",
            f"**Judge reason:** {reason}",
            "",
        ]
    lines += [f"**Caught {caught} of 3.**", ""]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nCaught {caught} of 3. Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
