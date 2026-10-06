"""The one event format live, fake, and replay all share (docs/ui-plan.md C).

EventLog turns Runner.run result segments into an append-only list of JSON
events. The dedupe rule is the same one evaluation.collect_calls needs: a
resumed segment repeats the pre-pause items with the same call_id
(scripts/probe_sdk.py, finding b), so each call_id becomes one tool_call
event and one tool_result event no matter how many segments repeat it.

run_with_pauses is run_interactive's loop (phishing_guard/runners.py:33)
with input() replaced by an awaited decision, so a browser click can arrive
mid-run over HTTP. It makes no judgments: it records whatever Guard did.

This module never imports the agents SDK, so the offline checks and the
fake server run without it ever loading.
"""

import json
import threading
from datetime import datetime, timezone

from phishing_guard.evaluation import reply_state
from phishing_guard.world import reset_world

# Mirrors phishing_guard/runners.py:19 without importing the SDK module.
MAX_PAUSES = 3


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_args(raw):
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return {"raw": raw}


class EventLog:
    """Append-only event list plus the derived phase.

    Appends happen on the runner's event loop thread; snapshots happen on
    HTTP handler threads, so the list is guarded by a lock. Events are never
    mutated after they are appended.
    """

    def __init__(self, mode, guard_commit):
        self.mode = mode
        self.guard_commit = guard_commit
        self.email_id = None
        self.phase = "idle"
        self._lock = threading.Lock()
        self._events = []
        self._seen_calls = set()
        self._seen_outputs = set()

    def _append(self, etype, **fields):
        with self._lock:
            event = {"seq": len(self._events), "type": etype, "at": _now()}
            event.update(fields)
            self._events.append(event)

    # ---- the event types (docs/ui-plan.md C) --------------------------------

    def case_started(self, email_id):
        self.email_id = email_id
        self.phase = "investigating"
        self._append("case_started", email_id=email_id, mode=self.mode,
                     guard_commit=self.guard_commit)

    def add_segment(self, result, email_id):
        """Extract events from one Runner.run result segment.

        Reads the same item shapes evaluation.collect_calls and
        collect_outputs read. Unknown tool names and any call order pass
        through unchanged (plan rule 6); repeats are dropped by call_id
        (plan rule 11).
        """
        for item in result.new_items:
            if item.type in ("tool_call_item", "tool_approval_item"):
                raw = item.raw_item
                if raw.type == "function_call" and raw.call_id not in self._seen_calls:
                    self._seen_calls.add(raw.call_id)
                    self._append("tool_call", call_id=raw.call_id, name=raw.name,
                                 args=_parse_args(raw.arguments))
            elif item.type == "tool_call_output_item":
                raw = item.raw_item
                call_id = raw["call_id"] if isinstance(raw, dict) else raw.call_id
                if call_id not in self._seen_outputs:
                    self._seen_outputs.add(call_id)
                    self._append("tool_result", call_id=call_id,
                                 output=str(item.output))
        for request in result.interruptions:
            call_id = getattr(getattr(request, "raw_item", None), "call_id", None)
            self._append("approval_request", call_id=call_id,
                         args=_parse_args(request.arguments))
        if result.interruptions:
            self.phase = "paused"

    def decision(self, decision, reason=None):
        self.phase = "finishing"
        self._append("decision", decision=decision, reason=reason)

    def truth(self, email_id):
        """Snapshot read directly from the world, never from the trace: a
        rejected move still leaves a tool_call_output_item (probe finding c),
        so folder and logs are the only honest record of what happened."""
        state = reply_state(email_id)
        self._append("truth", folder=state["folder"],
                     training_log=state["training_log"],
                     security_queue=state["security_queue"])

    def reply(self, text):
        self._append("reply", text=None if text is None else str(text))

    def done(self):
        self.phase = "done"
        self._append("run_done")

    def error(self, message, tb=None):
        self.phase = "error"
        self._append("run_error", message=message, traceback=tb)

    # ---- reading ------------------------------------------------------------

    def snapshot(self):
        with self._lock:
            return {"mode": self.mode, "guard_commit": self.guard_commit,
                    "email_id": self.email_id, "phase": self.phase,
                    "events": list(self._events)}


async def run_with_pauses(log, email_id, start_segment, resume_segment,
                          get_decision, max_pauses=MAX_PAUSES):
    """run_interactive's loop with the keyboard replaced by get_decision.

    start_segment() -> first result segment. resume_segment(result,
    decision, reason) -> the next segment after approve/reject is applied.
    get_decision() -> awaited (decision, reason) from the decision endpoint.
    The live versions (stage 3) wrap Runner.run / to_state / approve /
    reject exactly as runners.py does; the fake versions return canned
    segments. Event order: segment events, truth, decision, ... , reply,
    final truth, run_done.
    """
    reset_world()
    log.case_started(email_id)
    result = await start_segment()
    log.add_segment(result, email_id)
    for _ in range(max_pauses):
        if not result.interruptions:
            break
        log.truth(email_id)
        decision, reason = await get_decision()
        log.decision(decision, reason)
        result = await resume_segment(result, decision, reason)
        log.add_segment(result, email_id)
    log.reply(result.final_output)
    log.truth(email_id)
    log.done()
