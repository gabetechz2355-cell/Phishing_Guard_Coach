"""Tuesday end-of-day check: run every test case through Guard and score it.

For each case: run_case, score_case, the reply judge, append the row
(PLAN.md's run loop plus the tenth metric). Then the averages, the flag
metrics, the per-group breakdown, and the classifier-only baseline on the
same emails. Rows and summaries are saved under results/ so notebook 02
sections 8 and 9 can load them without rerunning. A case whose run raises
becomes an error row and the run goes on; the script exits non-zero if any
case errored, because the first pass is for finding harness bugs, not for
judging Guard.

The reply judge (phishing_guard/judge.py) asks, per case, whether Guard's
final reply claims something about what was done that contradicts the
email's final folder and log entries. --no-judge skips it. --no-save runs
without writing to results/ (for smoke tests).

Cost: one model call per Guard turn, about 7 to 9 per case, plus one judge
call per case, so a full 30-case pass is roughly 280 calls.

Run:  .venv/Scripts/python.exe scripts/tuesday_check.py [--cases C-01 C-02] [--tag name] [--verbose] [--no-judge] [--no-save]
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from phishing_guard.config import has_openai_key

if not has_openai_key():
    print("No OPENAI_API_KEY loaded from the environment or .env. Add it and rerun.")
    sys.exit(2)

from phishing_guard.classifier import load_classifier
from phishing_guard.evaluation import (METRIC_COLUMNS, classifier_baseline,
                                       results_table, run_all_cases,
                                       summarize, summarize_by_group,
                                       verdict_vs_classifier)
from phishing_guard.guard_agents import make_guard_full
from phishing_guard.judge import make_judge_fn
from phishing_guard.runners import run_case
from phishing_guard.world import TEST_CASES, reset_world

RESULTS_DIR = ROOT / "results"


def judge_mark(row):
    """One character for the reply judge: Y faithful, . contradiction,
    - not judged (no judge, judge error, or error row)."""
    f = row.get("reply_faithful")
    return "-" if f is None else ("Y" if f else ".")


def progress(row, verbose=False):
    marks = "".join("Y" if row[m] else "." for m in METRIC_COLUMNS) + "|" + judge_mark(row)
    status = "ERROR" if row.get("error") else marks
    print(f"  {row['case_id']}  {row['email_id']}  {row['category']:<12} "
          f"expected {row['expected_verdict']:<11} got {str(row['recorded_verdict']):<11} "
          f"{status}  ({row['tool_calls']} calls)")
    if row.get("error"):
        print("    " + row["error"].splitlines()[-1])
    elif verbose:
        print("    " + " > ".join(row["tool_sequence"]))
    if row.get("judge_error"):
        print("    judge: " + row["judge_error"].splitlines()[-1])
    elif verbose and row.get("judge_reason"):
        print("    judge: " + " ".join(row["judge_reason"].split()))


def print_summary(summary, by_group, table, baseline):
    print("\nAVERAGES over", summary["cases"], "cases")
    for m in METRIC_COLUMNS:
        print(f"  {m:<22} {summary[m]:.2f}")
    print(f"  {'flag precision':<22} {summary['flag_precision']:.2f}")
    print(f"  {'flag recall':<22} {summary['flag_recall']:.2f}")
    print(f"  {'flag F1':<22} {summary['flag_f1']:.2f}")
    print(f"  {'mean tool calls':<22} {summary['mean_tool_calls']:.1f}")
    print(f"  {'errors':<22} {summary['errors']}")
    if summary["judged"]:
        print(f"  {'reply_faithful':<22} {summary['reply_faithful']:.2f}  "
              f"(judge, over {summary['judged']} judged cases, "
              f"{summary['judge_errors']} judge errors)")
    else:
        print(f"  {'reply_faithful':<22} not judged")
    print("\nBY GROUP")
    print(by_group.round(2).to_string())
    print("\nAGENT vs CLASSIFIER ALONE on the same emails")
    print(table.round(2).to_string())
    print(f"  classifier ROC-AUC on these cases: {baseline['roc_auc']:.2f}")


async def main(case_ids, tag, verbose, use_judge=True, save=True):
    """Run, score, and judge the cases, print the tables, save under results/."""
    cases = {cid: TEST_CASES[cid] for cid in case_ids}
    guard = make_guard_full()
    judge = make_judge_fn() if use_judge else None
    print(f"Running {len(cases)} cases: {' '.join(cases)}"
          + ("" if use_judge else "  (no reply judge)"))
    print("  metric flags in order:", " ".join(METRIC_COLUMNS), "| reply_faithful (judge)")
    started = datetime.now()
    rows = await run_all_cases(guard, cases, run_case,
                               on_row=lambda r: progress(r, verbose), judge=judge)
    elapsed = (datetime.now() - started).total_seconds()

    summary = summarize(rows)
    by_group = summarize_by_group(rows)
    reset_world()
    baseline_rows, baseline = classifier_baseline(cases, load_classifier())
    table = results_table(summary, baseline)
    comparison = verdict_vs_classifier(rows, baseline_rows)
    print_summary(summary, by_group, table, baseline)

    failed = [r for r in rows if not all(r[m] for m in METRIC_COLUMNS)
              or r.get("reply_faithful") is False]
    if failed:
        print("\nCASES WITH A FAILED METRIC")
        for r in failed:
            misses = [m for m in METRIC_COLUMNS if not r[m]]
            if r.get("reply_faithful") is False:
                misses.append("reply_faithful")
            print(f"  {r['case_id']} ({r['category']}, expected {r['expected_verdict']}, "
                  f"got {r['recorded_verdict']}): {', '.join(misses)}")
            print("    " + " > ".join(r["tool_sequence"]))
            if r.get("reply_faithful") is False:
                print("    judge: " + " ".join((r.get("judge_reason") or "").split()))

    if not save:
        print(f"\nNot saved (--no-save), {elapsed:.0f}s.")
        sys.exit(1 if summary["errors"] else 0)

    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = started.strftime("%Y%m%d-%H%M%S")
    name = f"{stamp}-{tag}" if tag else stamp
    out = {"started": started.isoformat(timespec="seconds"), "elapsed_s": round(elapsed),
           "cases": list(cases), "summary": summary,
           "by_group": by_group.reset_index().to_dict(orient="records"),
           "baseline": baseline, "baseline_rows": baseline_rows, "rows": rows}
    (RESULTS_DIR / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (RESULTS_DIR / "latest.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    pd.DataFrame(rows).drop(columns=["final_output", "error"]).to_csv(
        RESULTS_DIR / f"{name}.csv", index=False)
    comparison.to_csv(RESULTS_DIR / f"{name}-vs-classifier.csv")
    print(f"\nSaved results/{name}.json, .csv, -vs-classifier.csv and results/latest.json "
          f"({elapsed:.0f}s).")
    sys.exit(1 if summary["errors"] else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", nargs="*", default=list(TEST_CASES),
                    help="case IDs to run (default: all)")
    ap.add_argument("--tag", default="", help="suffix for the results file name")
    ap.add_argument("--verbose", action="store_true", help="print each tool sequence")
    ap.add_argument("--no-judge", action="store_true", help="skip the reply judge")
    ap.add_argument("--no-save", action="store_true", help="do not write to results/")
    a = ap.parse_args()
    unknown = [c for c in a.cases if c not in TEST_CASES]
    if unknown:
        print("Unknown case IDs:", unknown)
        sys.exit(2)
    asyncio.run(main(a.cases, a.tag, a.verbose, use_judge=not a.no_judge, save=not a.no_save))
