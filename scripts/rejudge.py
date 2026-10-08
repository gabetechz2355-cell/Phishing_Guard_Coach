"""Re-run the reply judge only, over the replies and world states saved in a
results file. Guard and Coach are never built or called: the judge reads the
saved final reply and the saved final state (judge_state) and nothing else.

Used once after the baseline, when the judge's wording changed from yes/no to
CONTRADICTS/CONSISTENT, so the baseline could be re-judged by the same judge
that scores every later run. The source file is not touched. The new rows go
to <source>-rejudged.json and .csv, each row keeping the old judge's answer,
reason, and reply_faithful as old_*. results/latest.json is not touched.

Cost: one judge call per saved row (30 for the baseline).

Outputs are named <source>-rejudged-<tag>.json and .csv. The tag is required
and an existing output is never overwritten, so each judge version keeps its
own files (the first re-judge, with the word-first wording, is the untagged
<source>-rejudged.json).

Run:  .venv/Scripts/python.exe scripts/rejudge.py --tag reasonfirst [results/20261006-113554-baseline.json]
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from agents import Runner

from phishing_guard.evaluation import judge_result, summarize, summarize_by_group
from phishing_guard.judge import build_judge_input, make_judge

JUDGE_FIELDS = ("judge_answer", "judge_reason", "reply_faithful", "judge_error")


async def rejudge_row(judge, row):
    """New judge columns for one saved row. A row with no saved state or no
    reply (an error row) is left unjudged, as the live harness would."""
    state = row.get("judge_state")
    reply = row.get("final_output")
    if row.get("error") or not state:
        return judge_result(None, state=state)
    try:
        result = await Runner.run(judge, build_judge_input(state, reply), max_turns=2)
        return judge_result(result.final_output, state=state)
    except Exception as exc:  # judge trouble leaves the case unjudged
        import traceback
        return judge_result(None, state=state, error="".join(
            traceback.format_exception_only(type(exc), exc)).strip())


async def main(source, tag, note):
    """Re-judge every saved row, keep the old columns as old_*, save both."""
    name = f"{source.stem}-rejudged-{tag}"
    if any((source.parent / f"{name}{ext}").exists() for ext in (".json", ".csv")):
        print(f"results/{name}.* already exists; pick another --tag. Nothing was run.")
        sys.exit(2)
    old = json.loads(source.read_text(encoding="utf-8"))
    judge = make_judge()
    started = time.time()
    rows = []
    for old_row in old["rows"]:
        new_cols = await rejudge_row(judge, old_row)
        row = dict(old_row)
        for f in JUDGE_FIELDS:
            row["old_" + f] = old_row.get(f)
        row.update(new_cols)
        rows.append(row)
        mark = {True: "CONSISTENT", False: "CONTRADICTS", None: "not judged"}[row["reply_faithful"]]
        print(f"  {row['case_id']}  {row['category']:<12} old {str(row['old_judge_answer']):<4} -> {mark}")
    elapsed = time.time() - started

    summary = summarize(rows)
    by_group = summarize_by_group(rows)
    diffs = [{"case_id": r["case_id"], "category": r["category"],
              "old_answer": r["old_judge_answer"], "old_reply_faithful": r["old_reply_faithful"],
              "new_answer": r["judge_answer"], "new_reply_faithful": r["reply_faithful"]}
             for r in rows if r["old_reply_faithful"] != r["reply_faithful"]]

    out = {"source": source.name, "rejudged_elapsed_s": round(elapsed),
           "judge_wording": "CONTRADICTS or CONSISTENT (after the baseline; baseline used yes or no)",
           "old_summary": old["summary"], "summary": summary,
           "by_group": by_group.reset_index().to_dict(orient="records"),
           "changed_cases": diffs, "rows": rows}
    out["judge_wording"] = note or out["judge_wording"]
    out["tag"] = tag
    (source.parent / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    pd.DataFrame(rows).drop(columns=["final_output", "error", "judge_state"]).to_csv(
        source.parent / f"{name}.csv", index=False)

    print(f"\nreply_faithful: old {old['summary']['reply_faithful']:.3f} -> new {summary['reply_faithful']:.3f} "
          f"({summary['judged']} judged, {summary['judge_errors']} judge errors)")
    print(by_group[["reply_faithful", "cases"]].to_string())
    print(f"{len(diffs)} cases changed: " + ", ".join(d["case_id"] for d in diffs))
    print(f"\nSaved results/{name}.json and .csv ({elapsed:.0f}s). {source.name} and latest.json untouched.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Re-run the reply judge only over a saved results file.")
    ap.add_argument("source", nargs="?", default=str(ROOT / "results" / "20261006-113554-baseline.json"))
    ap.add_argument("--tag", required=True, help="suffix for the output files; an existing output is never overwritten")
    ap.add_argument("--note", default="", help="one line naming the judge wording used, saved in the output")
    a = ap.parse_args()
    asyncio.run(main(Path(a.source), a.tag, a.note))
