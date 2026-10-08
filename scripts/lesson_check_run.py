"""Judge the 10 hand-labeled lessons and compare with the hand labels.

Reads the hand labels and notes from results/lesson_check_inputs.md, but
builds each judge input from the source data (the mailbox, the answer key,
the user table, and the pass1 reply's lesson via the builder's extractor),
so the input holds only the email, the labeled red flags, the employee's
reason, the role, the lesson, and the computed word count — never the hand
labels or the Note lines. One judge call per lesson, ten in all.

Writes results/lesson_check.md: per case the four hand answers against the
four judge answers, agreement per criterion and overall, each disagreement
with the hand note and the judge's reason side by side, and a notes
section. The judge and the scorer modules are not edited by this script.

Run:  .venv/Scripts/python.exe scripts/lesson_check_run.py
"""

import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from agents import Runner
from lesson_check_build_inputs import extract_lesson

from phishing_guard.lesson_judge import (
    CRITERIA, build_lesson_judge_input, make_lesson_judge, parse_lesson_judge)
from phishing_guard.world import MAILBOX_ORIGINAL, TEST_CASES, USERS

SHEET = ROOT / "results" / "lesson_check_inputs.md"
OUTPUT = ROOT / "results" / "lesson_check.md"

HAND_LINE = re.compile(
    r"^## (C-\d+) \((E-\d+)\).*?"
    r"\*\*Hand labels \(yes/no\):\*\* names the labeled red flags: (YES|NO)\s+"
    r"gives a usable rule: (YES|NO)\s+invents nothing: (YES|NO)\s+"
    r"120 words or fewer: (YES|NO)\s*\n(?:\*\*Note:\*\* (.+))?",
    re.DOTALL | re.MULTILINE)

CRITERION_NAMES = {
    "FLAGS": "names the labeled red flags",
    "RULE": "gives a usable rule",
    "INVENTS_NOTHING": "invents nothing",
    "UNDER_120": "120 words or fewer",
}

NOTES = [
    "C-28 and C-29 are true-legitimate emails where the scripted employee "
    "rejected a cautious move, so Coach taught distrust of a real email. The "
    "lessons can still pass all four criteria; the criteria measure lesson "
    "quality, not verdict quality.",
    "The judge does not see Guard's tool evidence, only the email, the "
    "labeled red flags, the reason, and the role. That matters for "
    "INVENTS_NOTHING: a lesson detail drawn from tool output (C-09's \"link "
    "reputation unknown\") is unverifiable from the judge's inputs. In this "
    "run the judge let it pass, matching the hand label, but a stricter "
    "judge could mark such a detail invented; only the hand labels had the "
    "tool evidence in view.",
    "Some lessons put quotation marks around paraphrases rather than exact "
    "email text (C-05, C-24). The criteria judge grounding by meaning, so "
    "this is not an invention by itself, but it can read like a fabricated "
    "quote.",
]


def parse_hand_labels(text):
    """Case IDs, hand labels, and notes from the sheet; nothing else is read."""
    blocks = re.split(r"(?=^## C-)", text, flags=re.MULTILINE)[1:]
    cases = []
    for block in blocks:
        m = HAND_LINE.match(block)
        if not m:
            cid = block.split()[1] if len(block.split()) > 1 else "?"
            print(f"Could not parse the hand labels for {cid}; fix the sheet and rerun.")
            sys.exit(2)
        cid, eid, flags, rule, inv, u120, note = m.groups()
        cases.append({"case_id": cid, "email_id": eid,
                      "hand": {"FLAGS": flags, "RULE": rule,
                               "INVENTS_NOTHING": inv, "UNDER_120": u120},
                      "note": (note or "").strip() or None})
    return cases


def fmt(answers):
    """The four answers on one line, in criteria order."""
    return " ".join(f"{k}={answers[k]}" for k in CRITERIA) if answers else "unparseable"


async def main():
    """Judge each lesson, compare with the hand labels, write the report."""
    cases = parse_hand_labels(SHEET.read_text(encoding="utf-8"))
    pass1 = sorted(ROOT.glob("results/*-final-pass1.json"))
    if len(pass1) != 1:
        print(f"Expected one results/*-final-pass1.json, found {len(pass1)}.")
        sys.exit(2)
    rows = {r["case_id"]: r
            for r in json.loads(pass1[0].read_text(encoding="utf-8"))["rows"]}

    print(f"Judging {len(cases)} lessons, one call each.")
    judge = make_lesson_judge()
    agree_by = {k: 0 for k in CRITERIA}
    disagreements = []
    table = []
    for c in cases:
        case = TEST_CASES[c["case_id"]]
        email = MAILBOX_ORIGINAL[c["email_id"]]
        role = USERS[email["to_user"]]["role"]
        lesson = extract_lesson(rows[c["case_id"]]["final_output"] or "")
        result = await Runner.run(
            judge,
            build_lesson_judge_input(email, case["red_flags"],
                                     case["user_reason"], role, lesson),
            max_turns=2)
        parsed = parse_lesson_judge(result.final_output)
        answers = parsed["answers"] or {}
        marks = []
        for k in CRITERIA:
            same = answers.get(k) == c["hand"][k]
            if same:
                agree_by[k] += 1
            else:
                disagreements.append((c, k, answers.get(k), parsed["reason"]))
            marks.append("agree" if same else "DISAGREE")
        table.append((c["case_id"], c["hand"], answers, marks))
        print(f"{c['case_id']}  hand: {fmt(c['hand'])}")
        print(f"       judge: {fmt(answers)}  -> {marks.count('agree')}/4")

    total = sum(agree_by.values())
    lines = [
        "# Lesson judge vs hand labels, 10 reject cases",
        "",
        "One judge call per lesson from results/lesson_check_inputs.md, inputs "
        "rebuilt from the mailbox, the answer key, and the pass1 replies; the "
        "judge saw only the email, the labeled red flags, the employee's "
        "reason, the role, the lesson, and the computed word count — no hand "
        "labels and no notes. Criteria order: FLAGS (names the labeled red "
        "flags), RULE (gives a usable rule), INVENTS_NOTHING, UNDER_120.",
        "",
        "## Per case",
        "",
        "| Case | Hand | Judge | Agreement |",
        "|---|---|---|---|",
    ]
    for cid, hand, answers, marks in table:
        lines.append(f"| {cid} | {fmt(hand)} | {fmt(answers)} "
                     f"| {marks.count('agree')}/4 |")
    lines += [
        "",
        "## Agreement",
        "",
    ]
    for k in CRITERIA:
        lines.append(f"- {k} ({CRITERION_NAMES[k]}): {agree_by[k]} of 10")
    lines += [f"- **Overall: {total} of 40**", "", "## Disagreements", ""]
    if not disagreements:
        lines += ["None.", ""]
    for c, k, judge_ans, reason in disagreements:
        lines += [
            f"### {c['case_id']}, {k} ({CRITERION_NAMES[k]})",
            "",
            f"**Hand label:** {c['hand'][k]}"
            + (f" — note: {c['note']}" if c["note"] else ""),
            "",
            f"**Judge answer:** {judge_ans or 'unparseable'}",
            "",
            f"**Judge reason:** {' '.join((reason or '').split())}",
            "",
        ]
    lines += ["## Notes", ""]
    lines += [f"{i}. {n}" for i, n in enumerate(NOTES, 1)]
    lines.append("")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nOverall agreement {total} of 40. Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
