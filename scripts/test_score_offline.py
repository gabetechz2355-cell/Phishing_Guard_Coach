"""Offline checks for score_case, the run loop, and the summaries. No model.

Builds fake result segments shaped like the SDK's (new_items with
tool_call_item, tool_approval_item, tool_call_output_item; a repeated
pre-pause item after the resume, as scripts/probe_sdk.py found) and sets the
world state by hand, then asserts what each metric should say. Also runs
the classifier-only baseline on the real cases, which needs the joblib but
no API key.

Run:  .venv/Scripts/python.exe scripts/test_score_offline.py
"""

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phishing_guard.classifier import load_classifier
from phishing_guard.evaluation import (METRIC_COLUMNS, classifier_baseline,
                                       collect_calls, flag_metrics,
                                       results_table, run_all_cases,
                                       score_case, summarize,
                                       summarize_by_group,
                                       verdict_vs_classifier)
from phishing_guard.world import (MAILBOX, SECURITY_QUEUE, TEST_CASES,
                                  TRAINING_LOG, reset_world)

passed = failed = 0


def check(cond, label, detail=""):
    """Print a pass/fail line and count it; the script exits on the total."""
    global passed, failed
    if cond:
        passed += 1
        print(f"  [ok ] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label} {detail}")


# ---- fake trace builders ----------------------------------------------------

def _call(n, name, args, kind="tool_call_item"):
    """One fake tool-call (or approval) item with a deterministic call_id."""
    return SimpleNamespace(type=kind, raw_item=SimpleNamespace(
        type="function_call", name=name, arguments=json.dumps(args), call_id=f"call_{n}"))


def _output(n, text):
    """One fake tool-output item; raw_item is a dict, as the SDK returns it."""
    return SimpleNamespace(type="tool_call_output_item",
                           raw_item={"call_id": f"call_{n}"}, output=text)


def fake_results(calls, final_output="done", pause_at=None):
    """calls: list of (name, args). If pause_at is the index of the move,
    build two segments: the first ends with a tool_approval_item for it, the
    second repeats the call and approval items and adds the rest."""
    items = []
    for n, (name, args) in enumerate(calls):
        items.append(_call(n, name, args))
        if pause_at is not None and n == pause_at:
            items.append(_call(n, name, args, kind="tool_approval_item"))
            break
        items.append(_output(n, "ok"))
    if pause_at is None:
        return [SimpleNamespace(new_items=items, final_output=final_output,
                                interruptions=[])]
    seg1 = SimpleNamespace(new_items=items, final_output=None, interruptions=[object()])
    items2 = [_call(pause_at, *calls[pause_at]),
              _call(pause_at, *calls[pause_at], kind="tool_approval_item"),
              _output(pause_at, "moved")]
    for n in range(pause_at + 1, len(calls)):
        items2.append(_call(n, *calls[n]))
        items2.append(_output(n, "ok"))
    seg2 = SimpleNamespace(new_items=items2, final_output=final_output, interruptions=[])
    return [seg1, seg2]


def set_world(eid, verdict=None, folder="Inbox", logged=None, escalated=False):
    """Reset, then put one email's world state exactly where a test wants it."""
    reset_world()
    if verdict:
        MAILBOX[eid]["verdict"] = verdict
        MAILBOX[eid]["red_flags"] = ["x"]
    MAILBOX[eid]["folder"] = folder
    if logged:
        TRAINING_LOG.append({"user_id": MAILBOX[eid]["to_user"],
                             "email_id": eid, "outcome": logged})
    if escalated:
        SECURITY_QUEUE.append({"email_id": eid, "summary": "s"})


E1, E2, E3 = "E-001", "E-002", "E-003"
C1, C2, C3 = TEST_CASES["C-01"], TEST_CASES["C-02"], TEST_CASES["C-03"]
link1 = MAILBOX[E1]["links"][0]
u1, u2 = MAILBOX[E1]["to_user"], MAILBOX[E2]["to_user"]

APPROVE_TRACE = [
    ("classify_email_text", {"email_id": E1}),
    ("check_sender_domain", {"domain": MAILBOX[E1]["from_addr"].split("@")[1]}),
    ("check_url", {"url": link1}),
    ("get_user_profile", {"user_id": u1}),
    ("record_verdict", {"email_id": E1, "verdict": "phishing", "red_flags": ["a"]}),
    ("move_to_phishing_folder", {"email_id": E1, "reason": "r"}),
    ("log_training_event", {"user_id": u1, "email_id": E1, "outcome": "reported"}),
]
REJECT_TRACE = [
    ("classify_email_text", {"email_id": E2}),
    ("check_sender_domain", {"domain": "apex-supp1y.example"}),
    ("get_user_profile", {"user_id": u2}),
    ("record_verdict", {"email_id": E2, "verdict": "phishing", "red_flags": ["a"]}),
    ("move_to_phishing_folder", {"email_id": E2, "reason": "r"}),
    ("coach_user", {"input": "lesson please"}),
    ("log_training_event", {"user_id": u2, "email_id": E2, "outcome": "missed"}),
    ("escalate_to_security", {"email_id": E2, "summary": "s"}),
]
LEGIT_TRACE = [
    ("classify_email_text", {"email_id": E3}),
    ("check_sender_domain", {"domain": "apexsupply.example"}),
    ("check_url", {"url": MAILBOX[E3]["links"][0]}),
    ("get_user_profile", {"user_id": u1}),
    ("record_verdict", {"email_id": E3, "verdict": "legitimate", "red_flags": []}),
]


def all_true(score):
    """True when every code-scored metric in the score dict passed."""
    return all(score[m] for m in METRIC_COLUMNS)


print("collect_calls dedupes the repeated pre-pause items")
res = fake_results(APPROVE_TRACE, pause_at=5)
check(len(res) == 2 and len(collect_calls(res)) == 7, "7 unique calls over 2 segments",
      f"got {len(collect_calls(res))}")

print("\n1. C-01 approve, perfect trace and world")
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, res)
check(all_true(s) and s["flagged"] and s["tool_calls"] == 7, "every metric True", str(s))

print("\n2. C-02 reject, perfect trace: coach, missed, escalated, stays in Inbox")
set_world(E2, "phishing", "Inbox", "missed", escalated=True)
s = score_case(C2, fake_results(REJECT_TRACE, pause_at=4))
check(all_true(s) and s["flagged"], "every metric True", str(s))

print("\n3. C-03 legitimate, no move, nothing logged")
set_world(E3, "legitimate")
s = score_case(C3, fake_results(LEGIT_TRACE))
check(all_true(s) and not s["flagged"], "every metric True, not flagged", str(s))

print("\n4. wrong verdict followed faithfully: adherence passes, completion fails")
# Guard calls E-003 suspicious; the scripted decision is None so run_case
# rejects; Guard then coaches, logs missed, escalates. Faithful to its verdict.
trace = LEGIT_TRACE[:4] + [
    ("record_verdict", {"email_id": E3, "verdict": "suspicious", "red_flags": ["a"]}),
    ("move_to_phishing_folder", {"email_id": E3, "reason": "r"}),
    ("coach_user", {"input": "x"}),
    ("log_training_event", {"user_id": u1, "email_id": E3, "outcome": "missed"}),
    ("escalate_to_security", {"email_id": E3, "summary": "s"}),
]
set_world(E3, "suspicious", "Inbox", "missed", escalated=True)
s = score_case(C3, fake_results(trace, pause_at=5))
check(not s["verdict_correct"], "verdict_correct False")
check(s["workflow_adherence"], "workflow_adherence True", str(s))
check(not s["task_completion"], "task_completion False")
check(s["flagged"], "flagged True")

print("\n5. move before verdict breaks workflow adherence only")
trace = APPROVE_TRACE[:4] + [APPROVE_TRACE[5], APPROVE_TRACE[4], APPROVE_TRACE[6]]
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=4))
check(not s["workflow_adherence"] and s["task_completion"] and s["tool_correctness"],
      "adherence False, completion and tools True", str(s))

print("\n6. no record_verdict at all")
trace = [c for c in APPROVE_TRACE if c[0] != "record_verdict"]
set_world(E1, None, "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=4))
check(not s["verdict_correct"] and not s["workflow_adherence"] and not s["flagged"],
      "verdict, adherence, flagged all False", str(s))

print("\n7. the same tool twice with the same arguments")
trace = APPROVE_TRACE[:1] + APPROVE_TRACE
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=6))
check(not s["step_efficiency"] and s["workflow_adherence"], "efficiency False, adherence True", str(s))

print("\n8. wrong domain argument, and a url not in the email")
trace = list(APPROVE_TRACE)
trace[1] = ("check_sender_domain", {"domain": "microsoft.com"})
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=5))
check(not s["argument_correctness"], "wrong domain -> argument_correctness False")
trace = list(APPROVE_TRACE)
trace[2] = ("check_url", {"url": "https://example.com/not-in-email"})
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=5))
check(not s["argument_correctness"], "foreign url -> argument_correctness False")
trace = list(APPROVE_TRACE)
trace[1] = ("check_sender_domain", {"domain": " " + MAILBOX[E1]["from_addr"].split("@")[1].upper() + " "})
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=5))
check(s["argument_correctness"], "case and whitespace in the domain are tolerated")

print("\n9. forbidden tool (check_url on the no-link case) and a missing required tool")
trace = REJECT_TRACE[:3] + [("check_url", {"url": "https://x.example"})] + REJECT_TRACE[3:]
set_world(E2, "phishing", "Inbox", "missed", escalated=True)
s = score_case(C2, fake_results(trace, pause_at=5))
check(not s["tool_correctness"] and not s["argument_correctness"],
      "forbidden tool -> tool_correctness False (and its url is foreign)", str(s))
trace = [c for c in REJECT_TRACE if c[0] != "get_user_profile"]
set_world(E2, "phishing", "Inbox", "missed", escalated=True)
s = score_case(C2, fake_results(trace, pause_at=3))
check(not s["tool_correctness"] and s["workflow_adherence"],
      "missing required tool -> tool_correctness False, adherence still True", str(s))

print("\n10. action tool with the wrong email id")
trace = list(APPROVE_TRACE)
trace[6] = ("log_training_event", {"user_id": u1, "email_id": E2, "outcome": "reported"})
set_world(E1, "phishing", "Phishing", "reported")
s = score_case(C1, fake_results(trace, pause_at=5))
check(not s["argument_correctness"], "wrong email_id -> argument_correctness False")

print("\n11. run_all_cases keeps going past a case that raises, and summarize counts it")


async def fake_run_case(guard, case):
    """Stand-in run_case: C-02 raises, the others return canned traces."""
    eid = case["email_id"]
    if eid == E2:
        raise RuntimeError("boom")
    if eid == E1:
        set_world(E1, "phishing", "Phishing", "reported")
        return fake_results(APPROVE_TRACE, pause_at=5)
    set_world(E3, "legitimate")
    return fake_results(LEGIT_TRACE)


seen = []
rows = asyncio.run(run_all_cases(None, {k: TEST_CASES[k] for k in ("C-01", "C-02", "C-03")},
                                 fake_run_case, on_row=lambda r: seen.append(r["case_id"])))
check(seen == ["C-01", "C-02", "C-03"], "three rows, in order", str(seen))
bad = rows[1]
check(bad["error"] and "boom" in bad["error"] and not any(bad[m] for m in METRIC_COLUMNS),
      "error row carries the traceback and every metric False")
check(rows[0]["tool_sequence"][-1] == "log_training_event" and rows[0]["segments"] == 2,
      "good row carries tool_sequence and segment count")
summ = summarize(rows)
check(summ["errors"] == 1 and summ["cases"] == 3, "summary counts 1 error of 3", str(summ))
check(abs(summ["task_completion"] - 2 / 3) < 1e-9, "task_completion mean 2/3", str(summ))
# flagged: C-01 True (phishing), C-02 False (error), C-03 False (legit)
check(summ["flag_precision"] == 1.0 and summ["flag_recall"] == 0.5, "flag P 1.0, R 0.5", str(summ))
grp = summarize_by_group(rows)
check(list(grp.index) == ["clear_phish", "clear_legit"] and grp.loc["clear_phish", "cases"] == 2,
      "per-group table groups and counts", str(grp))

print("\n12. flag_metrics by hand")
fm = flag_metrics([True, True, False, False], ["phishing", "legitimate", "phishing", "legitimate"])
check(fm["precision"] == 0.5 and fm["recall"] == 0.5 and fm["f1"] == 0.5 and fm["tn"] == 1,
      "P=R=F1=0.5, tn=1", str(fm))
fm = flag_metrics([False, False], ["phishing", "legitimate"])
check(fm == {"precision": 0.0, "recall": 0.0, "f1": 0.0, "tp": 0, "fp": 0, "fn": 1, "tn": 1},
      "nothing flagged -> zeros, no division error", str(fm))

print("\n13. classifier-only baseline on the real cases (joblib, no API)")
reset_world()
clf = load_classifier()
brows, bm = classifier_baseline(TEST_CASES, clf)
check(len(brows) == len(TEST_CASES) and bm["n"] == len(TEST_CASES), f"{len(TEST_CASES)} rows")
check(0 <= bm["f1"] <= 1 and 0 <= bm["roc_auc"] <= 1, "metrics in range", str(bm))
print(f"     classifier alone at 0.5: P {bm['precision']:.2f}  R {bm['recall']:.2f}  "
      f"F1 {bm['f1']:.2f}  AUC {bm['roc_auc']:.2f}  "
      f"(tp {bm['tp']} fp {bm['fp']} fn {bm['fn']} tn {bm['tn']})")
flagged_ids = [r["email_id"] for r in brows if r["flagged"]]
print("     flags:", flagged_ids)
tbl = results_table({"flag_precision": 1.0, "flag_recall": 0.9, "flag_f1": 0.95}, bm)
check(list(tbl.index) == ["Guard + tools", "classifier alone (0.5)"], "results_table rows")
cmp = verdict_vs_classifier(rows[:1] + rows[2:], [r for r in brows if r["case_id"] in ("C-01", "C-03")])
check(list(cmp.index) == ["C-01", "C-03"] and "clf_prob" in cmp, "verdict_vs_classifier joins on case_id")

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
