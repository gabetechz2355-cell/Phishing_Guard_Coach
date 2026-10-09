"""Offline check for the UI server: fake runner, real HTTP, no API calls.

Starts the server in-process on an ephemeral 127.0.0.1 port with the fake
runner at zero delay, drives cases C, A (approve), B (reject), the odd run
E-010, and a failing runner, and checks the event stream, the dedupe rule,
the truth strips, resets, and the error path. The style follows
scripts/test_score_offline.py: check(cond, label), exit 1 on any failure.

Run:  .venv/Scripts/python.exe ui/dev/check_offline.py
"""

import http.client
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from phishing_guard.world import MAILBOX
from ui.dev.fake_runner import REJECTION_PREFIX, make_fake_runner
from ui.server import App, make_server

PASS = FAIL = 0


def check(cond, label, detail=""):
    global PASS, FAIL
    mark = "ok " if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{mark}] {label}" + (f": {detail}" if detail and not cond else ""))


def serve(app):
    server = make_server(app, 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    # Hard guard: these checks drive starts, decisions, and resets, so they
    # must never run against a live server. The script builds its own fake
    # in-process server today; this keeps a future edit honest too.
    _, state = api(port, "GET", "/api/state")
    if state.get("mode") != "fake":
        print(f"ABORT: server reports mode {state.get('mode')!r}, not 'fake'.")
        sys.exit(1)
    return server, port


def api(port, method, path, body=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    payload = None if body is None else json.dumps(body)
    headers = {"Content-Type": "application/json"} if payload else {}
    conn.request(method, path, body=payload, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    try:
        return resp.status, json.loads(raw)
    except ValueError:
        return resp.status, raw


def wait_phase(port, phases, timeout=5.0):
    """Wait for a phase; on 'paused', also wait for its truth event, which
    lands just after the phase flips."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _, state = api(port, "GET", "/api/state")
        if state["phase"] in phases:
            if state["phase"] == "paused" and (
                    not state["events"]
                    or state["events"][-1]["type"] != "truth"):
                time.sleep(0.02)
                continue
            return state
        time.sleep(0.02)
    raise TimeoutError(f"phase never reached {phases}; last: {state['phase']}")


def of_type(events, etype):
    return [e for e in events if e["type"] == etype]


def call_names(events):
    return [e["name"] for e in of_type(events, "tool_call")]


def main():
    app = App(make_fake_runner(delay=0.0), mode="fake")
    _, port = serve(app)

    print("\n1. basics")
    status, _ = api(port, "GET", "/")
    check(status == 200, "GET / serves a page")
    status, _ = api(port, "GET", "/api/nope")
    check(status == 404, "unknown route is 404")
    status, _ = api(port, "POST", "/api/start", {"case": "Z"})
    check(status == 400, "unknown case is 400")
    status, _ = api(port, "POST", "/api/decision", {"decision": "approve"})
    check(status == 409, "decision with nothing pending is 409")
    _, state = api(port, "GET", "/api/state")
    check(state["phase"] == "idle" and state["events"] == [],
          "initial state is idle and empty")
    check(state["mode"] == "fake", "mode is reported", state["mode"])
    check(bool(state["guard_commit"]) and state["guard_commit"] != "unknown",
          "guard commit is a real hash", state["guard_commit"])
    check(len(state["mailbox"]) == 3
          and all(m["folder"] == "Inbox" for m in state["mailbox"]),
          "mailbox lists the three demo emails, all in Inbox")

    print("\n2. case C (E-003): legitimate, no pause")
    status, body = api(port, "POST", "/api/start", {"case": "C"})
    check(status == 200 and body.get("started") == "E-003", "start accepted")
    state = wait_phase(port, ("done", "error"))
    ev = state["events"]
    check(state["phase"] == "done", "run finished", state["phase"])
    check(ev[0]["type"] == "case_started" and ev[0]["email_id"] == "E-003"
          and ev[0]["mode"] == "fake" and bool(ev[0]["guard_commit"]),
          "case_started carries email, mode, commit")
    check(call_names(ev) == ["classify_email_text", "check_sender_domain",
                             "check_url", "get_user_profile",
                             "record_verdict"],
          "tool_call order is the canned order", str(call_names(ev)))
    check(not of_type(ev, "approval_request") and not of_type(ev, "decision"),
          "no pause and no decision on a legitimate email")
    calls = {e["call_id"] for e in of_type(ev, "tool_call")}
    outs = {e["call_id"] for e in of_type(ev, "tool_result")}
    check(calls == outs, "every tool_call has exactly one tool_result")
    check(ev[-3]["type"] == "reply" and bool(ev[-3]["text"])
          and ev[-2]["type"] == "truth" and ev[-1]["type"] == "run_done",
          "run ends reply, truth, run_done")
    check(ev[-2]["folder"] == "Inbox" and ev[-2]["training_log"] == []
          and ev[-2]["security_queue"] == [],
          "truth: Inbox, empty logs")
    check(state["truth"]["folder"] == "Inbox", "live truth matches")
    seqs = [e["seq"] for e in ev]
    check(seqs == list(range(len(ev))), "seq is dense and ordered")

    status, _ = api(port, "POST", "/api/reset")
    check(status == 200, "reset accepted")
    _, state = api(port, "GET", "/api/state")
    check(state["phase"] == "idle" and state["events"] == [],
          "reset returns to idle")

    print("\n3. case A (E-001): phishing, approve")
    api(port, "POST", "/api/start", {"case": "A"})
    state = wait_phase(port, ("paused", "done", "error"))
    check(state["phase"] == "paused", "run paused for approval", state["phase"])
    ev = state["events"]
    reqs = of_type(ev, "approval_request")
    check(len(reqs) == 1 and reqs[0]["args"]["email_id"] == "E-001"
          and bool(reqs[0]["args"]["reason"]),
          "approval_request carries Guard's reason")
    moves = [e for e in of_type(ev, "tool_call")
             if e["name"] == "move_to_phishing_folder"]
    check(len(moves) == 1 and moves[0]["call_id"] == reqs[0]["call_id"],
          "one move tool_call, same call_id as the request")
    check(moves[0]["call_id"] not in
          {e["call_id"] for e in of_type(ev, "tool_result")},
          "the move has no result while paused")
    check(ev[-1]["type"] == "truth" and ev[-1]["folder"] == "Inbox",
          "paused truth: still Inbox")
    status, _ = api(port, "POST", "/api/start", {"case": "B"})
    check(status == 409, "second start while running is 409")

    status, _ = api(port, "POST", "/api/decision", {"decision": "approve"})
    check(status == 200, "approve accepted")
    state = wait_phase(port, ("done", "error"))
    ev = state["events"]
    check(state["phase"] == "done", "run finished after approve")
    dec = of_type(ev, "decision")
    check(len(dec) == 1 and dec[0]["decision"] == "approve",
          "decision event recorded")
    outs = {e["call_id"]: e["output"] for e in of_type(ev, "tool_result")}
    check("moved to the Phishing folder" in outs.get(moves[0]["call_id"], ""),
          "move result arrived after approval")
    names = call_names(ev)
    check(names.count("move_to_phishing_folder") == 1
          and len(names) == len(set(e["call_id"]
                                    for e in of_type(ev, "tool_call"))),
          "repeated pre-pause items were deduped", str(names))
    check(names[-1] == "log_training_event", "follow-up logged after the move")
    check(ev[-2]["type"] == "truth" and ev[-2]["folder"] == "Phishing"
          and [r["outcome"] for r in ev[-2]["training_log"]] == ["reported"]
          and ev[-2]["security_queue"] == [],
          "final truth: Phishing, reported, no ticket")
    status, _ = api(port, "POST", "/api/decision", {"decision": "approve"})
    check(status == 409, "decision after the run is 409")
    api(port, "POST", "/api/reset")

    print("\n4. case B (E-002): phishing, reject with a typed reason")
    reason = "That's Apex, we pay them every month."
    api(port, "POST", "/api/start", {"case": "B"})
    state = wait_phase(port, ("paused", "done", "error"))
    check(state["phase"] == "paused", "run paused for approval")
    check("check_url" not in call_names(state["events"]),
          "no link check on the no-link email")
    status, _ = api(port, "POST", "/api/decision",
                    {"decision": "reject", "reason": reason})
    check(status == 200, "reject accepted")
    state = wait_phase(port, ("done", "error"))
    ev = state["events"]
    check(state["phase"] == "done", "run finished after reject")
    dec = of_type(ev, "decision")
    check(dec and dec[0]["decision"] == "reject" and dec[0]["reason"] == reason,
          "decision event keeps the typed reason")
    outs = {e["call_id"]: e["output"] for e in of_type(ev, "tool_result")}
    move_id = next(e["call_id"] for e in of_type(ev, "tool_call")
                   if e["name"] == "move_to_phishing_folder")
    check(outs[move_id] == REJECTION_PREFIX + reason,
          "rejected move's output is the rejection message")
    names = call_names(ev)
    check(names[-3:] == ["coach_user", "log_training_event",
                         "escalate_to_security"],
          "reject follow-up: coach, log, escalate", str(names))
    coach_id = next(e["call_id"] for e in of_type(ev, "tool_call")
                    if e["name"] == "coach_user")
    check("Accounts Payable" in outs[coach_id],
          "the lesson is the coach tool's output")
    log_id = next(e["call_id"] for e in of_type(ev, "tool_call")
                  if e["name"] == "log_training_event")
    check("training simulation" in outs[log_id],
          "the simulation reveal rides the log result")
    esc_id = next(e["call_id"] for e in of_type(ev, "tool_call")
                  if e["name"] == "escalate_to_security")
    check(outs[esc_id] == "Escalated as SEC-001.", "escalation ticket issued")
    check(len({e["call_id"] for e in of_type(ev, "tool_call")}) == len(names)
          == 8, "eight unique tool calls, repeats deduped", str(names))
    reply = of_type(ev, "reply")[0]["text"]
    check("training simulation" in reply, "reply shown with the reveal")
    check(ev[-2]["folder"] == "Inbox"
          and [r["outcome"] for r in ev[-2]["training_log"]] == ["missed"]
          and len(ev[-2]["security_queue"]) == 1,
          "final truth: Inbox, missed, one ticket")
    api(port, "POST", "/api/reset")

    print("\n5. odd run (E-010): unknown tool, suspicious, early stop")
    status, _ = api(port, "POST", "/api/start", {"email_id": "E-010"})
    check(status == 200, "start by raw email_id accepted")
    state = wait_phase(port, ("done", "error"))
    ev = state["events"]
    check(state["phase"] == "done", "odd run finished", state["phase"])
    check("lookup_dns_history" in call_names(ev),
          "unknown tool name passes through untouched")
    odd_id = next(e["call_id"] for e in of_type(ev, "tool_call")
                  if e["name"] == "lookup_dns_history")
    odd_out = next(e for e in of_type(ev, "tool_result")
                   if e["call_id"] == odd_id)
    check(odd_out.get("data") == {"error": "no such tool in the real system"},
          "python-repr tool output parsed into the data field",
          str(odd_out.get("data")))
    verdict = next(e for e in of_type(ev, "tool_call")
                   if e["name"] == "record_verdict")
    check(verdict["args"]["verdict"] == "suspicious", "suspicious verdict")
    check(not of_type(ev, "approval_request"),
          "early stop: no approval requested")
    check(ev[-2]["folder"] == "Inbox" and ev[-2]["training_log"] == [],
          "truth: nothing happened to the mailbox")
    check(any(m["email_id"] == "E-010" for m in state["mailbox"]),
          "mailbox summary includes the odd current email")
    api(port, "POST", "/api/reset")

    print("\n6. failing runner: the error path")
    app2 = App(make_fake_runner(delay=0.0, fail=True), mode="fake")
    _, port2 = serve(app2)
    api(port2, "POST", "/api/start", {"case": "A"})
    state = wait_phase(port2, ("error",))
    ev = state["events"]
    err = of_type(ev, "run_error")
    check(state["phase"] == "error", "phase is error")
    check(err and "fake API failure" in err[0]["message"],
          "run_error carries the message")
    check(bool(err[0]["traceback"]), "traceback kept for the evidence log")
    status, _ = api(port2, "POST", "/api/reset")
    check(status == 200, "reset works after an error")
    _, state = api(port2, "GET", "/api/state")
    check(state["phase"] == "idle", "back to idle after the error")

    print("\n7. world hygiene")
    check(all(MAILBOX[e]["folder"] == "Inbox" for e in MAILBOX),
          "every email is back in the Inbox after the checks")

    print(f"\n{PASS} passed, {FAIL} failed.")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
