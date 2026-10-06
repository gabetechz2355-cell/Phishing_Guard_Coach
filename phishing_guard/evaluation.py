"""Trace reading and scoring.

Monday: collect_calls and expected_follow_up, both PLAN.md verbatim, plus
collect_outputs for reading tool results (the Coach's lesson, the
simulation reveal) straight from the trace.
Tuesday: score_case (PLAN.md verbatim), the run loop over every test case,
the summary tables, and the classifier-only baseline. Also the harness side
of the tenth metric, reply faithfulness: reply_state (what the judge sees),
parse_judge_answer, judge_result, and a judge hook in run_all_cases. The
judge agent itself lives in judge.py so this module never imports the SDK.
The lesson judge and the three-pass run are scheduled for Wednesday to
Friday.
"""

import json
import traceback

import pandas as pd

from .world import MAILBOX, SECURITY_QUEUE, TRAINING_LOG

EVIDENCE = {"classify_email_text", "check_sender_domain", "check_url", "get_user_profile"}
ID_TOOLS = {"record_verdict", "move_to_phishing_folder",
            "log_training_event", "escalate_to_security"}

# The code-scored per-case metrics, in PLAN.md's table order. Flag precision,
# recall, and F1 come from the flagged column, so they are not listed here.
METRIC_COLUMNS = ["verdict_correct", "workflow_adherence", "task_completion",
                  "tool_correctness", "argument_correctness", "step_efficiency"]

# The judge-scored per-case metric (end-to-end). Kept apart from
# METRIC_COLUMNS because it is None, not False, when no judge ran.
JUDGE_COLUMNS = ["reply_faithful"]

# Kaggle held-out split, from 01_train_classifier.ipynb (train_and_save on
# 2026-10-04, seed 42, 16,416 held-out rows). Kept here so the Results
# section can show the baseline row without retraining.
KAGGLE_HOLDOUT_METRICS = {"precision": 0.984, "recall": 0.987,
                          "f1": 0.985, "roc_auc": 0.999, "n": 16416}


def collect_calls(results):
    """Unique function calls across every result segment, in order.

    A paused run holds a tool_call_item and a tool_approval_item with the
    same call_id, and the resumed segment repeats both, so dedupe by call_id.
    """
    calls = {}
    for result in results:
        for item in result.new_items:
            if item.type in ("tool_call_item", "tool_approval_item"):
                raw = item.raw_item
                if raw.type == "function_call" and raw.call_id not in calls:
                    calls[raw.call_id] = {"name": raw.name,
                                          "args": json.loads(raw.arguments)}
    return list(calls.values())


def collect_call_ids(results):
    """call_ids in the same order collect_calls returns them."""
    ids = []
    for result in results:
        for item in result.new_items:
            if item.type in ("tool_call_item", "tool_approval_item"):
                raw = item.raw_item
                if raw.type == "function_call" and raw.call_id not in ids:
                    ids.append(raw.call_id)
    return ids


def collect_outputs(results):
    """call_id -> tool output string, across every segment."""
    outputs = {}
    for result in results:
        for item in result.new_items:
            if item.type == "tool_call_output_item":
                raw = item.raw_item
                call_id = raw["call_id"] if isinstance(raw, dict) else raw.call_id
                outputs[call_id] = item.output
    return outputs


def expected_follow_up(verdict, decision):
    """One row of the HITL table: (folder, logged outcome, coach, escalated)."""
    if verdict == "legitimate":
        return ("Inbox", None, False, False)
    if decision == "approve":
        return ("Phishing", "reported", False, verdict == "suspicious")
    return ("Inbox", "missed", True, True)


# ---- Tuesday: reply faithfulness, harness side ------------------------------

def reply_state(email_id):
    """What actually happened to one email: its folder and its entries in
    the training log and the security queue. This, plus Guard's final
    reply, is everything the reply judge sees. Read it right after the run,
    before the next reset_world()."""
    return {"email_id": email_id,
            "folder": MAILBOX[email_id]["folder"],
            "training_log": [r for r in TRAINING_LOG if r["email_id"] == email_id],
            "security_queue": [q for q in SECURITY_QUEUE if q["email_id"] == email_id]}


# The judge's answer words. The baseline judge answered yes (contradiction) or
# no; its wording was replaced after the baseline by CONTRADICTS or CONSISTENT
# because "yes" was read as "yes, it matches". Both are still parsed, so rows
# saved with the old words keep loading.
CONTRADICTION_WORDS = ("yes", "contradicts")
FAITHFUL_WORDS = ("no", "consistent")


def parse_judge_answer(text):
    """The judge's one-word answer, lowercased, from the first word of its
    reply: 'contradicts' or 'consistent' (current wording), 'yes' or 'no'
    (the baseline wording), or None if the first word is none of these."""
    if not text or not text.strip():
        return None
    first = text.strip().split()[0].strip(".,:;!?*\"'()").lower()
    return first if first in CONTRADICTION_WORDS + FAITHFUL_WORDS else None


def judge_result(answer_text, state=None, error=None):
    """The judge columns for one row.

    The judge says whether the reply's claims about actions contradict the
    state. So reply_faithful is True on 'consistent' (or the old 'no'), False
    on 'contradicts' (or the old 'yes'), and None when there is no usable
    answer (not judged). An unparseable answer is recorded in judge_error so
    it can be read later.
    """
    answer = parse_judge_answer(answer_text)
    if answer is None and answer_text and not error:
        error = "unparseable judge answer: " + answer_text.strip()[:200]
    return {"judge_answer": answer,
            "judge_reason": answer_text.strip() if answer_text else None,
            "judge_state": state,
            "judge_error": error,
            "reply_faithful": None if answer is None else answer in FAITHFUL_WORDS}


# ---- Tuesday: scoring -------------------------------------------------------

def score_case(case, results):
    """Call right after run_case, before the next reset_world().

    PLAN.md verbatim. Reads the verdict and the folder from MAILBOX and the
    follow-ups from the two logs, not from the trace, because a rejected move
    still leaves a tool_call_output_item carrying the rejection message.
    """
    calls = collect_calls(results)
    names = [c["name"] for c in calls]
    eid = case["email_id"]
    email = MAILBOX[eid]
    verdict = email.get("verdict")

    # Order: all evidence, then the verdict, then any move.
    i_verdict = names.index("record_verdict") if "record_verdict" in names else -1
    i_move = (names.index("move_to_phishing_folder")
              if "move_to_phishing_folder" in names else len(names))
    i_evidence = [i for i, n in enumerate(names) if n in EVIDENCE]
    order_ok = bool(i_evidence) and max(i_evidence) < i_verdict < i_move

    # What actually happened in the world.
    logged = [r["outcome"] for r in TRAINING_LOG if r["email_id"] == eid]
    state = (email["folder"], logged[-1] if logged else None,
             "coach_user" in names,
             any(q["email_id"] == eid for q in SECURITY_QUEUE))

    domain = email["from_addr"].split("@")[-1].lower()
    args_ok = all(
        (c["name"] != "check_sender_domain"
             or c["args"].get("domain", "").lower().strip() == domain)
        and (c["name"] != "check_url"
             or c["args"].get("url", "").strip() in email["links"])
        and (c["name"] not in ID_TOOLS or c["args"].get("email_id") == eid)
        for c in calls)
    seen = [(c["name"], json.dumps(c["args"], sort_keys=True)) for c in calls]

    return {
        "verdict_correct": verdict == case["expected_verdict"],
        "flagged": verdict in ("suspicious", "phishing"),
        "workflow_adherence": order_ok and state == expected_follow_up(
            verdict, case["user_decision"]),
        "task_completion": state == expected_follow_up(
            case["expected_verdict"], case["user_decision"]),
        "tool_correctness": set(case["required_tools"]) <= set(names)
            and not set(names) & set(case["forbidden_tools"]),
        "argument_correctness": args_ok,
        "step_efficiency": len(seen) == len(set(seen)),
        "tool_calls": len(calls),
        "final_output": results[-1].final_output,
    }


def _identity(case_id, case):
    email = MAILBOX[case["email_id"]]
    return {"case_id": case_id, "email_id": case["email_id"],
            "category": case["category"], "true_label": case["true_label"],
            "expected_verdict": case["expected_verdict"],
            "recorded_verdict": email.get("verdict"),
            "user_decision": case["user_decision"],
            "is_simulation": bool(email.get("is_simulation"))}


def make_row(case_id, case, score, results=None):
    """One results-table row: the score plus the case's identity and what
    Guard recorded, so the table can be read without the trace."""
    row = _identity(case_id, case)
    row.update(score)
    row["error"] = None
    row.update(judge_result(None))   # judge columns present, None until judged
    if results is not None:
        row["tool_sequence"] = [c["name"] for c in collect_calls(results)]
        row["segments"] = len(results)
    return row


def error_row(case_id, case, exc):
    """A row for a case whose run raised. Every metric is False so the
    failure counts against the agent instead of being dropped. The
    traceback is kept so harness bugs can be told apart from agent errors."""
    row = _identity(case_id, case)
    row.update({"flagged": False, "tool_calls": 0, "final_output": None,
                "tool_sequence": [], "segments": 0,
                "error": "".join(traceback.format_exception(exc)).strip()})
    for m in METRIC_COLUMNS:
        row[m] = False
    row.update(judge_result(None))   # no reply to judge: not judged, None
    return row


async def run_all_cases(guard, cases, run_case, on_row=None, judge=None):
    """The run loop: run_case, then score_case, then the judge, then append.

    `cases` is the TEST_CASES dict (or a subset of it). `run_case` is passed
    in so this module does not import the runners (and the SDK) just to
    score a trace. A case whose run raises gets an error_row instead of
    stopping the loop, because PLAN.md's first pass is for finding harness
    bugs. `on_row` is called with each row as it lands, for progress output.

    `judge`, if given, is an async callable (case, results) -> the judge
    columns from judge_result. It runs right after score_case, while the
    case's world state is still in place (judge.make_judge_fn builds the
    live one). A judge that raises leaves the case unjudged (reply_faithful
    None) with the traceback in judge_error; it never fails the case.
    """
    rows = []
    for case_id, case in cases.items():
        try:
            results = await run_case(guard, case)
            row = make_row(case_id, case, score_case(case, results), results)
            if judge is not None:
                try:
                    row.update(await judge(case, results))
                except Exception as exc:  # judge trouble is not Guard's fault
                    row.update(judge_result(
                        None, error="".join(traceback.format_exception(exc)).strip()))
        except Exception as exc:  # one bad case must not end the 30-case run
            row = error_row(case_id, case, exc)
        rows.append(row)
        if on_row:
            on_row(row)
    return rows


# ---- Tuesday: summaries -----------------------------------------------------

def flag_metrics(flagged, true_label):
    """Precision, recall, F1 of 'flagged' against the true label, plus the
    confusion counts. Same definitions as the proposal's classifier metrics."""
    flagged = [bool(f) for f in flagged]
    truth = [t == "phishing" for t in true_label]
    tp = sum(f and t for f, t in zip(flagged, truth))
    fp = sum(f and not t for f, t in zip(flagged, truth))
    fn = sum(not f and t for f, t in zip(flagged, truth))
    tn = sum(not f and not t for f, t in zip(flagged, truth))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def summarize(rows):
    """The averages: one value per metric over all rows, plus the flag
    metrics, the mean tool-call count, and the error count. Returns a dict."""
    df = pd.DataFrame(rows)
    out = {m: float(df[m].astype(bool).mean()) for m in METRIC_COLUMNS}
    fm = flag_metrics(df["flagged"], df["true_label"])
    out.update({"flag_precision": fm["precision"], "flag_recall": fm["recall"],
                "flag_f1": fm["f1"]})
    out["mean_tool_calls"] = float(df["tool_calls"].mean())
    out["cases"] = int(len(df))
    out["errors"] = int(df["error"].notna().sum()) if "error" in df else 0
    # Reply faithfulness averages over judged rows only. Rows saved before
    # the metric existed have no column at all; unjudged rows hold None.
    judged = df["reply_faithful"].notna() if "reply_faithful" in df else pd.Series(False, index=df.index)
    out["reply_faithful"] = (float(df.loc[judged, "reply_faithful"].astype(bool).mean())
                             if judged.any() else float("nan"))
    out["judged"] = int(judged.sum())
    out["judge_errors"] = int(df["judge_error"].notna().sum()) if "judge_error" in df else 0
    return out


def summarize_by_group(rows):
    """Per-category breakdown: the mean of each metric within clear_phish,
    clear_legit, and borderline, with the case count. Returns a DataFrame."""
    df = pd.DataFrame(rows)
    for m in METRIC_COLUMNS:
        df[m] = df[m].astype(bool)
    g = df.groupby("category")
    table = g[METRIC_COLUMNS].mean()
    if "reply_faithful" in df:
        table["reply_faithful"] = g["reply_faithful"].apply(
            lambda s: s.dropna().astype(bool).mean() if s.notna().any() else float("nan"))
    table["tool_calls"] = g["tool_calls"].mean()
    table["cases"] = g.size()
    order = [c for c in ("clear_phish", "clear_legit", "borderline") if c in table.index]
    return table.loc[order]


def results_table(agent_summary, baseline):
    """Agent versus classifier alone on the same cases: precision, recall,
    F1. Returns a two-row DataFrame."""
    return pd.DataFrame([
        {"system": "Guard + tools", "precision": agent_summary["flag_precision"],
         "recall": agent_summary["flag_recall"], "f1": agent_summary["flag_f1"]},
        {"system": "classifier alone (0.5)", "precision": baseline["precision"],
         "recall": baseline["recall"], "f1": baseline["f1"]},
    ]).set_index("system")


# ---- Tuesday: classifier-only baseline --------------------------------------

def classifier_baseline(cases, clf, threshold=0.5):
    """Run the classifier alone on the same emails. Returns the per-email
    rows (probability, flagged, true label) and the summary metrics with
    ROC-AUC over the cases. The classifier sees subject + body, as the
    classify_email_text tool does."""
    from sklearn.metrics import roc_auc_score

    rows = []
    for case_id, case in cases.items():
        e = MAILBOX[case["email_id"]]
        prob = float(clf.predict_proba([e["subject"] + " " + e["body"]])[0][1])
        rows.append({"case_id": case_id, "email_id": case["email_id"],
                     "category": case["category"], "true_label": case["true_label"],
                     "prob": prob, "flagged": prob >= threshold})
    metrics = flag_metrics([r["flagged"] for r in rows], [r["true_label"] for r in rows])
    truth = [r["true_label"] == "phishing" for r in rows]
    metrics["roc_auc"] = (float(roc_auc_score(truth, [r["prob"] for r in rows]))
                          if len(set(truth)) == 2 else float("nan"))
    metrics["threshold"] = threshold
    metrics["n"] = len(rows)
    return rows, metrics


def verdict_vs_classifier(agent_rows, baseline_rows):
    """Side-by-side per case: the classifier's probability and the agent's
    verdict, so the report can point at the cases where they differ."""
    a = pd.DataFrame(agent_rows).set_index("case_id")
    b = pd.DataFrame(baseline_rows).set_index("case_id")
    out = a[["email_id", "category", "true_label", "expected_verdict"]].copy()
    out["clf_prob"] = b["prob"].round(2)
    out["clf_flagged"] = b["flagged"]
    out["agent_verdict"] = a["recorded_verdict"]
    out["agent_flagged"] = a["flagged"].astype(bool)
    out["verdict_correct"] = a["verdict_correct"].astype(bool)
    out["task_completion"] = a["task_completion"].astype(bool)
    return out
