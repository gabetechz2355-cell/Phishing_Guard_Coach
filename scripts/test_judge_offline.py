"""Offline checks for the reply-faithfulness harness, with a stubbed judge.

Covers the harness side of the tenth metric with no model: what the judge
is shown (reply_state, build_judge_input), how its answer is read
(parse_judge_answer, judge_result), how run_all_cases calls it and survives
it failing, and how the summaries average it over judged rows only. The
judge agent itself is not run here; scripts/tuesday_check.py runs it live.

Run:  .venv/Scripts/python.exe scripts/test_judge_offline.py
"""

import asyncio
import math
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phishing_guard.config import lm_model
from phishing_guard.evaluation import (JUDGE_COLUMNS, METRIC_COLUMNS,
                                       judge_result, parse_judge_answer,
                                       reply_state, run_all_cases, summarize,
                                       summarize_by_group)
from phishing_guard.judge import JUDGE_INSTRUCTIONS, build_judge_input, make_judge
from phishing_guard.world import MAILBOX, SECURITY_QUEUE, TEST_CASES, TRAINING_LOG, reset_world

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


def fake_results(final_output):
    """The smallest result list the harness accepts: one segment, no tool
    items, a final reply. score_case scores it all-False, which is fine
    here; only the judge path is under test."""
    return [SimpleNamespace(new_items=[], final_output=final_output, interruptions=[])]


E1, E2, E3 = "E-001", "E-002", "E-003"
C1, C2, C3 = TEST_CASES["C-01"], TEST_CASES["C-02"], TEST_CASES["C-03"]

print("1. reply_state reads only this email's folder and log entries")
reset_world()
MAILBOX[E2]["folder"] = "Inbox"
MAILBOX[E1]["folder"] = "Phishing"
TRAINING_LOG.append({"user_id": "U-01", "email_id": E2, "outcome": "missed"})
TRAINING_LOG.append({"user_id": "U-03", "email_id": E1, "outcome": "reported"})
SECURITY_QUEUE.append({"email_id": E2, "summary": "lookalike vendor"})
s2 = reply_state(E2)
s1 = reply_state(E1)
s3 = reply_state(E3)
check(s2["folder"] == "Inbox" and s2["training_log"] == [TRAINING_LOG[0]]
      and s2["security_queue"] == [SECURITY_QUEUE[0]], "E-002: Inbox, 1 log row, 1 queue row", str(s2))
check(s1["folder"] == "Phishing" and s1["training_log"] == [TRAINING_LOG[1]]
      and s1["security_queue"] == [], "E-001: Phishing, 1 log row, empty queue", str(s1))
check(s3 == {"email_id": E3, "folder": "Inbox", "training_log": [], "security_queue": []},
      "E-003: untouched email has empty lists", str(s3))

print("\n2. parse_judge_answer reads the first word only")
for text, want in [("Yes. The reply says moved but the folder is Inbox.", "yes"),
                   ("no\nEvery claim matches the state.", "no"),
                   ("NO, nothing contradicts it.", "no"),
                   ("**Yes** - escalation claimed, queue empty.", "yes"),
                   ("Maybe; the reply is vague.", None),
                   ("", None), ("   ", None), (None, None)]:
    check(parse_judge_answer(text) == want, f"{text!r:<55} -> {want}", str(parse_judge_answer(text)))

print("\n3. judge_result maps the answer to reply_faithful")
r = judge_result("no\nAll claims match.", state={"folder": "Inbox"})
check(r["reply_faithful"] is True and r["judge_answer"] == "no" and r["judge_error"] is None
      and r["judge_state"] == {"folder": "Inbox"}, "'no' -> faithful True, no error", str(r))
r = judge_result("Yes, it claims a move that did not happen.")
check(r["reply_faithful"] is False and r["judge_answer"] == "yes", "'yes' -> faithful False", str(r))
r = judge_result("Unclear.")
check(r["reply_faithful"] is None and r["judge_answer"] is None
      and r["judge_error"].startswith("unparseable judge answer"), "unparseable -> None, error noted", str(r))
r = judge_result(None)
check(r["reply_faithful"] is None and r["judge_error"] is None and r["judge_reason"] is None,
      "no answer at all -> all None (not judged)", str(r))
r = judge_result(None, error="boom")
check(r["reply_faithful"] is None and r["judge_error"] == "boom", "explicit error kept", str(r))
check(set(JUDGE_COLUMNS) <= set(r), "JUDGE_COLUMNS are judge_result keys")

print("\n4. run_all_cases calls the judge while the case's world state is still in place")
seen_states = {}


async def fake_run_case(guard, case):
    """Stand-in run_case: sets each email's world state and returns a canned
    reply, so the stub judges have something true or false to check."""
    reset_world()
    eid = case["email_id"]
    if eid == E2:   # reject path: stays in Inbox, logged missed, escalated
        TRAINING_LOG.append({"user_id": "U-01", "email_id": eid, "outcome": "missed"})
        SECURITY_QUEUE.append({"email_id": eid, "summary": "s"})
        return fake_results("I moved it to the Phishing folder, but you rejected the warning.")
    if eid == E3:   # legitimate: nothing happens
        return fake_results("This invoice looks legitimate. No action was taken.")
    MAILBOX[eid]["folder"] = "Phishing"   # approve path
    TRAINING_LOG.append({"user_id": "U-03", "email_id": eid, "outcome": "reported"})
    return fake_results("Moved to the Phishing folder and logged.")


async def stub_judge(case, results):
    """A toy first-word judge that also records the state it was shown."""
    state = reply_state(case["email_id"])
    seen_states[case["case_id"]] = state
    reply = results[-1].final_output
    # A toy judge: a move claim with the email still in Inbox is a contradiction.
    claims_move = "moved" in reply.lower()
    answer = "yes\nclaims a move" if claims_move and state["folder"] == "Inbox" else "no\nmatches"
    return judge_result(answer, state=state)


cases = {k: dict(TEST_CASES[k], case_id=k) for k in ("C-01", "C-02", "C-03")}
rows = asyncio.run(run_all_cases(None, cases, fake_run_case, judge=stub_judge))
by_id = {r["case_id"]: r for r in rows}
check(set(seen_states) == {"C-01", "C-02", "C-03"}, "judge called once per case", str(list(seen_states)))
check(seen_states["C-01"]["folder"] == "Phishing" and seen_states["C-02"]["folder"] == "Inbox"
      and seen_states["C-02"]["security_queue"], "judge saw each case's own state before the next reset")
check(by_id["C-01"]["reply_faithful"] is True, "C-01 approve reply faithful", str(by_id["C-01"]["judge_answer"]))
check(by_id["C-02"]["reply_faithful"] is False and by_id["C-02"]["judge_answer"] == "yes",
      "C-02 'I moved it' with folder Inbox -> contradiction", str(by_id["C-02"]["judge_answer"]))
check(by_id["C-03"]["reply_faithful"] is True, "C-03 'no action was taken' faithful")
check(all(set(JUDGE_COLUMNS) <= set(r) and "judge_state" in r for r in rows), "judge columns on every row")
check(all(m in by_id["C-02"] for m in METRIC_COLUMNS), "code metrics untouched by the judge")

print("\n5. run_all_cases without a judge leaves the metric None on every row")
rows_nj = asyncio.run(run_all_cases(None, cases, fake_run_case))
check(all(r["reply_faithful"] is None and r["judge_answer"] is None for r in rows_nj),
      "reply_faithful None, judge_answer None")

print("\n6. a judge that raises leaves the case unjudged and the run going")


async def broken_judge(case, results):
    """A judge that raises on C-02, to prove one judge failure is contained."""
    if case["email_id"] == E2:
        raise RuntimeError("kaboom")
    return judge_result("no\nfine")


rows_b = asyncio.run(run_all_cases(None, cases, fake_run_case, judge=broken_judge))
b = {r["case_id"]: r for r in rows_b}
check(len(rows_b) == 3, "three rows")
check(b["C-02"]["reply_faithful"] is None and "kaboom" in b["C-02"]["judge_error"]
      and b["C-02"]["error"] is None, "C-02 unjudged with the traceback, case not an error row")
check(b["C-01"]["reply_faithful"] is True and b["C-03"]["reply_faithful"] is True, "the other two judged")

print("\n7. a case whose run raises is not judged")


async def exploding_run_case(guard, case):
    """A run_case that always raises, to produce an error row."""
    raise RuntimeError("run failed")


rows_e = asyncio.run(run_all_cases(None, {"C-01": cases["C-01"]}, exploding_run_case, judge=stub_judge))
check(rows_e[0]["error"] and rows_e[0]["reply_faithful"] is None and rows_e[0]["judge_error"] is None,
      "error row: reply_faithful None, no judge error")

print("\n8. summarize averages reply_faithful over judged rows only")
summ = summarize(rows)
check(summ["judged"] == 3 and abs(summ["reply_faithful"] - 2 / 3) < 1e-9 and summ["judge_errors"] == 0,
      "3 judged, mean 2/3, 0 judge errors", str({k: summ[k] for k in ("judged", "reply_faithful", "judge_errors")}))
summ_b = summarize(rows_b)
check(summ_b["judged"] == 2 and summ_b["reply_faithful"] == 1.0 and summ_b["judge_errors"] == 1,
      "broken judge: 2 judged, mean 1.0, 1 judge error", str({k: summ_b[k] for k in ("judged", "reply_faithful", "judge_errors")}))
summ_nj = summarize(rows_nj)
check(summ_nj["judged"] == 0 and math.isnan(summ_nj["reply_faithful"]), "no judge: 0 judged, NaN mean")
old_rows = [{k: v for k, v in r.items() if k not in ("reply_faithful", "judge_answer", "judge_reason",
                                                     "judge_state", "judge_error")} for r in rows]
summ_old = summarize(old_rows)
check(summ_old["judged"] == 0 and math.isnan(summ_old["reply_faithful"]) and summ_old["judge_errors"] == 0,
      "rows saved before the metric existed still summarize")
check(all(abs(summ[m] - summ_old[m]) < 1e-9 for m in METRIC_COLUMNS), "code metrics unchanged by the judge columns")

print("\n9. summarize_by_group carries reply_faithful, NaN where nothing was judged")
grp = summarize_by_group(rows_b)
check("reply_faithful" in grp.columns, "column present")
check(grp.loc["clear_legit", "reply_faithful"] == 1.0, "clear_legit judged 1.0")
check(grp.loc["clear_phish", "reply_faithful"] == 1.0, "clear_phish: C-01 judged True, C-02 unjudged -> 1.0 over judged")
grp_nj = summarize_by_group(rows_nj)
check(grp_nj["reply_faithful"].isna().all(), "nothing judged -> NaN per group")
grp_old = summarize_by_group(old_rows)
check("reply_faithful" not in grp_old.columns and list(grp_old["cases"]) == [2, 1],
      "old rows: no column, groups intact")

print("\n9b. CONTRADICTS and CONSISTENT, with the old yes/no still parsed")
for text, want in [("CONTRADICTS\nIt says moved but the folder is Inbox.", "contradicts"),
                   ("CONSISTENT\nEvery claim matches.", "consistent"),
                   ("consistent", "consistent"), ("Contradicts.", "contradicts"),
                   ("**CONSISTENT** - matches.", "consistent"),
                   ("  \nCONTRADICTS", "contradicts"),
                   ("CONSISTENT-ish", None), ("Inconsistent", None), ("Contradiction found", None),
                   ("yes", "yes"), ("No", "no")]:
    check(parse_judge_answer(text) == want, f"{text!r:<45} -> {want}", str(parse_judge_answer(text)))
r = judge_result("CONSISTENT\nThe reply says moved and the folder is Phishing.", state={"folder": "Phishing"})
check(r["reply_faithful"] is True and r["judge_answer"] == "consistent" and r["judge_error"] is None
      and r["judge_state"] == {"folder": "Phishing"}, "CONSISTENT -> faithful True, answer kept as written", str(r))
r = judge_result("CONTRADICTS\nSays moved; folder is Inbox.")
check(r["reply_faithful"] is False and r["judge_answer"] == "contradicts", "CONTRADICTS -> faithful False", str(r))
r = judge_result("Inconsistent\nnot one of the two words")
check(r["reply_faithful"] is None and r["judge_answer"] is None
      and r["judge_error"].startswith("unparseable judge answer"), "a near-miss word is unparseable, not a verdict", str(r))
check(judge_result("no\nok")["reply_faithful"] is True and judge_result("yes\nbad")["reply_faithful"] is False,
      "old yes/no still map: no -> True, yes -> False")


async def new_word_judge(case, results):
    """The stub judge again, answering with the CONTRADICTS/CONSISTENT words."""
    state = reply_state(case["email_id"])
    claims_move = "moved" in results[-1].final_output.lower()
    return judge_result("CONTRADICTS\nclaims a move" if claims_move and state["folder"] == "Inbox"
                        else "CONSISTENT\nmatches", state=state)


rows_new = asyncio.run(run_all_cases(None, cases, fake_run_case, judge=new_word_judge))
bn = {r["case_id"]: r for r in rows_new}
check(bn["C-01"]["reply_faithful"] is True and bn["C-02"]["reply_faithful"] is False
      and bn["C-03"]["reply_faithful"] is True, "run_all_cases with the new words: C-01 True, C-02 False, C-03 True")
sn = summarize(rows_new)
check(sn["judged"] == 3 and abs(sn["reply_faithful"] - 2 / 3) < 1e-9 and sn["judge_errors"] == 0,
      "summarize averages new-word rows the same way", str(sn["reply_faithful"]))

print("\n9c. reason first, then a last line 'ANSWER: CONTRADICTS' or 'ANSWER: CONSISTENT'")
for text, want in [("The reply claims a move; the folder is Inbox. They do not match.\nANSWER: CONTRADICTS", "contradicts"),
                   ("Claim: moved to Phishing. State: folder Phishing. They match.\nANSWER: CONSISTENT", "consistent"),
                   ("Claims match.\nanswer: consistent", "consistent"),
                   ("Claims match.\nANSWER: CONSISTENT.", "consistent"),
                   ("Claims match.\n**ANSWER: CONSISTENT**", "consistent"),
                   ("Claims match.\nANSWER:CONTRADICTS", "contradicts"),
                   ("Claims match.\nANSWER: CONSISTENT\n\n  ", "consistent"),
                   # the last line wins over a reasoning paragraph that starts with an answer-like word
                   ("Consistent wording, but the move claim fails against Inbox.\nANSWER: CONTRADICTS", "contradicts"),
                   ("No claim about an action is made.\nANSWER: CONSISTENT", "consistent"),
                   ("Yes, the reply says moved but the folder is Inbox.\nANSWER: CONTRADICTS", "contradicts"),
                   # an ANSWER line that is not a clean last line is unparseable, never read by its first word
                   ("Consistent so far.\nANSWER: CONSISTENT\nOne more thing.", None),
                   ("Consistent so far.\nANSWER: CONSISTENT because it matches", None),
                   ("Consistent so far.\nANSWER: INCONSISTENT", None),
                   ("Consistent so far.\nANSWER: MAYBE", None),
                   ("Consistent so far.\nANSWER:", None),
                   # no ANSWER line at all: the older formats still parse
                   ("CONTRADICTS\nIt says moved but the folder is Inbox.", "contradicts"),
                   ("yes\nclaims a move", "yes"), ("no\nmatches", "no"),
                   ("Reasoning with no answer line.", None)]:
    got = parse_judge_answer(text)
    check(got == want, f"{text.splitlines()[-1]!r:<44} -> {want}", f"{got}  for {text!r}")
r = judge_result("Claim: moved. State: Inbox. No match.\nANSWER: CONTRADICTS", state={"folder": "Inbox"})
check(r["reply_faithful"] is False and r["judge_answer"] == "contradicts" and r["judge_error"] is None
      and r["judge_reason"].startswith("Claim: moved."), "ANSWER: CONTRADICTS -> faithful False, whole reasoning kept", str(r))
r = judge_result("Claim: moved. State: Phishing. Match.\nANSWER: CONSISTENT")
check(r["reply_faithful"] is True and r["judge_answer"] == "consistent", "ANSWER: CONSISTENT -> faithful True", str(r))
r = judge_result("Claims match.\nANSWER: CONSISTENT because yes")
check(r["reply_faithful"] is None and r["judge_error"].startswith("unparseable judge answer"),
      "a malformed ANSWER line is an unparseable answer with an error, not a verdict", str(r))


async def answer_line_judge(case, results):
    """The stub judge again, answering in the reason-first ANSWER-line format."""
    # The strict rule in miniature: "moved ... rejected" with the folder still Inbox is a contradiction;
    # "offered ... rejected" is not.
    state = reply_state(case["email_id"])
    reply = results[-1].final_output.lower()
    asserts_move = "moved" in reply and "offered" not in reply
    bad = asserts_move and state["folder"] == "Inbox"
    return judge_result("Reasoning paragraph.\nANSWER: " + ("CONTRADICTS" if bad else "CONSISTENT"), state=state)


rows_al = asyncio.run(run_all_cases(None, cases, fake_run_case, judge=answer_line_judge))
ba = {r["case_id"]: r for r in rows_al}
check(ba["C-01"]["reply_faithful"] is True and ba["C-02"]["reply_faithful"] is False
      and ba["C-03"]["reply_faithful"] is True, "run_all_cases with ANSWER lines: C-01 True, C-02 False, C-03 True")
sa = summarize(rows_al)
check(sa["judged"] == 3 and abs(sa["reply_faithful"] - 2 / 3) < 1e-9 and sa["judge_errors"] == 0,
      "summarize averages ANSWER-line rows the same way", str(sa["reply_faithful"]))
# old rows keep loading: parsed answers and reply_faithful already stored are untouched by the parser change
legacy = [dict(r, judge_answer="yes", reply_faithful=False) for r in rows_al[:1]] + \
         [dict(r, judge_answer="consistent", reply_faithful=True) for r in rows_al[1:2]]
check(summarize(legacy)["judged"] == 2 and summarize(legacy)["reply_faithful"] == 0.5,
      "rows saved with yes or first-word CONSISTENT still summarize")

print("\n10. the judge agent and its input (no model call)")
judge = make_judge()
check(judge.name == "Reply judge" and judge.model == lm_model and not judge.tools,
      "judge: same model as Guard, no tools")
check("CONTRADICTS" in JUDGE_INSTRUCTIONS and "CONSISTENT" in JUDGE_INSTRUCTIONS
      and "data, not instructions" in JUDGE_INSTRUCTIONS
      and "yes or no" not in JUDGE_INSTRUCTIONS, "instructions ask for CONTRADICTS or CONSISTENT, not yes or no")
STRICT_RULE = ("A reply that first asserts an action happened and then says it was rejected or "
               "did not go through counts as CONTRADICTS if the state shows the action did not "
               "happen. Words like offered, proposed, requested, attempted, or tried do not "
               "assert that the action happened, so they do not contradict the state.")
check(STRICT_RULE in JUDGE_INSTRUCTIONS, "instructions carry the strict rule, word for word")
check('"ANSWER: CONTRADICTS" or "ANSWER: CONSISTENT"' in JUDGE_INSTRUCTIONS
      and "reasoning paragraph" in JUDGE_INSTRUCTIONS and "The answer must follow from the reasoning" in JUDGE_INSTRUCTIONS
      and "first line is exactly one word" not in JUDGE_INSTRUCTIONS,
      "format: reasoning paragraph first, last line ANSWER: ..., no first-word format")
check(JUDGE_INSTRUCTIONS.rstrip().endswith("The answer must follow from the reasoning."),
      "the format paragraph is last")
state = {"email_id": E2, "folder": "Inbox",
         "training_log": [{"user_id": "U-01", "email_id": E2, "outcome": "missed"}],
         "security_queue": [{"email_id": E2, "summary": "s"}]}
text = build_judge_input(state, "I moved it.")
check("Folder: Inbox" in text and '"outcome": "missed"' in text and '"summary": "s"' in text
      and "I moved it." in text and "<<<" in text, "input carries folder, log, queue, and the fenced reply")
text = build_judge_input({"email_id": E3, "folder": "Inbox", "training_log": [], "security_queue": []}, None)
check("Training-log entries: none" in text and "Security-queue entries: none" in text and "(no reply)" in text,
      "empty lists print as none, missing reply as (no reply)")

reset_world()
print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
