"""Build the lesson hand-check sheet. Offline: no API calls, no judge.

Reads results/*-final-pass1.json, takes every case whose scripted decision
was reject and whose reply carries a Coach lesson, and writes
results/lesson_check_inputs.md: case ID, email subject, sender, and full
body, the labeled red flags from the answer key, the employee's stated
reason for rejecting, the employee role, the lesson text, and a blank
hand-label line with one yes/no box per lesson-judge criterion (PLAN.md
spec: names the labeled red flags, gives a usable rule, invents nothing,
120 words or fewer). No judge output appears
on the sheet; label by hand before running any judge.

The lesson is the part of Guard's final reply from the "Lesson:" header, or
from the first numbered item, to the end. Reject cases without a lesson
(for example a legitimate verdict, so no move was offered and Coach never
ran) are listed at the top and get no section.

Run:  .venv/Scripts/python.exe scripts/lesson_check_build_inputs.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from phishing_guard.world import MAILBOX_ORIGINAL, TEST_CASES, USERS

RESULTS = sorted(ROOT.glob("results/*-final-pass1.json"))
OUTPUT = ROOT / "results" / "lesson_check_inputs.md"

LESSON_START = re.compile(r"^(?:\*\*)?Lesson:?(?:\*\*)?\s*$|^1[).]\s", re.MULTILINE)

BOXES = ("names the labeled red flags: ___   gives a usable rule: ___   "
         "invents nothing: ___   120 words or fewer: ___")


def extract_lesson(reply: str) -> str | None:
    m = LESSON_START.search(reply)
    if not m:
        return None
    lesson = reply[m.start():]
    lesson = re.sub(r"^(?:\*\*)?Lesson:?(?:\*\*)?\s*\n+", "", lesson)
    return lesson.strip()


def main():
    if len(RESULTS) != 1:
        print(f"Expected one results/*-final-pass1.json, found {len(RESULTS)}.")
        sys.exit(2)
    data = json.loads(RESULTS[0].read_text(encoding="utf-8"))
    rejects = [r for r in data["rows"] if r["user_decision"] == "reject"]

    sections, missing = [], []
    for row in rejects:
        email = MAILBOX_ORIGINAL[row["email_id"]]
        case = TEST_CASES[row["case_id"]]
        role = USERS[email["to_user"]]["role"]
        lesson = extract_lesson(row["final_output"] or "")
        if lesson is None:
            missing.append(f"{row['case_id']} ({row['email_id']}, "
                           f"verdict {row['recorded_verdict']})")
            continue
        words = len(lesson.split())
        flags = "; ".join(case["red_flags"]) if case["red_flags"] else "none"
        sections.append("\n".join([
            f"## {row['case_id']} ({row['email_id']})",
            "",
            f"**Subject:** {email['subject'] or '(blank)'}",
            f"**Sender:** {email['from_name']} <{email['from_addr']}>",
            f"**Employee role:** {role}",
            "",
            "**Body:**",
            "",
            "```",
            email["body"].strip(),
            "```",
            "",
            f"**Labeled red flags:** {flags}",
            "",
            f"**Employee's reason for rejecting:** {case['user_reason'] or 'none given'}",
            "",
            f"**Lesson ({words} words):**",
            "",
            lesson,
            "",
            f"**Hand labels (yes/no):** {BOXES}",
            "",
        ]))

    header = [
        "# Lesson hand-check inputs, reject cases, no judge",
        "",
        f"Lessons from {RESULTS[0].name} (run started {data['started']}), one "
        "per reject case whose reply carries a Coach lesson, with the email "
        "body, the answer key's red flags, and the employee's stated reason "
        "beside each. Label each box by hand before looking at any judge "
        "output. Criteria per PLAN.md: "
        "the lesson names the labeled red flags, gives a usable rule, invents "
        "nothing, and stays at 120 words or fewer. Word counts are computed "
        "here, not judged.",
        "",
    ]
    if missing:
        header += ["Reject cases with no lesson in the reply: "
                   + "; ".join(missing) + ".", ""]

    OUTPUT.write_text("\n".join(header) + "\n" + "\n".join(sections),
                      encoding="utf-8")
    print(f"{len(rejects)} reject cases; {len(sections)} lessons on the sheet; "
          f"{len(missing)} without a lesson"
          + (f" ({'; '.join(missing)})" if missing else "") + ".")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
