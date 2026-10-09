"""Thin local server for the Phishing Guard UI (docs/ui-plan.md, rule 3).

Three actions and a reset, no judgments of its own:
    POST /api/start     {"case": "A"} or {"email_id": "E-001"}
    POST /api/decision  {"decision": "approve"|"reject", "reason": "..."}
    GET  /api/state     mode, commit, phase, events, truth, mailbox
    POST /api/reset     cancel the run, reset_world(), clean slate

Standard library only. Listens on 127.0.0.1 only. The HTTP handlers run on
ThreadingHTTPServer threads; the agent run lives on one background asyncio
loop thread, and the decision crosses over through an asyncio.Queue.

Run (offline, no API):  .venv/Scripts/python.exe ui/server.py --fake
Live mode arrives in stage 3 of the plan.
"""

import argparse
import asyncio
import json
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from phishing_guard.evaluation import reply_state
from phishing_guard.world import MAILBOX, USERS, reset_world
from ui.events import EventLog

GIT_EXE = r"C:\Program Files\Git\cmd\git.exe"
DEMO_CASES = {"A": "E-001", "B": "E-002", "C": "E-003"}
INDEX_PATH = Path(__file__).resolve().parent / "index.html"
PLACEHOLDER = ("<!doctype html><title>Phishing Guard UI</title>"
               "<p>ui/index.html is not built yet (plan stage 2). "
               "The API is up: GET /api/state</p>")


def guard_commit():
    """The commit the running code comes from, for the mode badge (rule 8)."""
    try:
        out = subprocess.run([GIT_EXE, "rev-parse", "--short", "HEAD"],
                             cwd=ROOT, capture_output=True, text=True,
                             timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except OSError:
        pass
    return "unknown"


def mailbox_summary(current_email_id=None):
    """The three demo emails (plus the current one, if odd) read straight
    from MAILBOX and USERS. is_simulation is left out on purpose: the page
    learns it only from a tool result, the way the employee would."""
    ids = list(DEMO_CASES.values())
    if current_email_id and current_email_id in MAILBOX \
            and current_email_id not in ids:
        ids.append(current_email_id)
    out = []
    for key_or_none, eid in [(k, v) for k, v in DEMO_CASES.items()] + \
            [(None, i) for i in ids[3:]]:
        e = MAILBOX[eid]
        u = USERS[e["to_user"]]
        out.append({"case": key_or_none, "email_id": eid,
                    "from_name": e["from_name"], "from_addr": e["from_addr"],
                    "reply_to": e["reply_to"], "subject": e["subject"],
                    "body": e["body"], "links": e["links"],
                    "folder": e["folder"],
                    "to": {"name": u["name"], "role": u["role"]}})
    return out


class App:
    """Owns the background asyncio loop, the current run, and its EventLog."""

    RUNNING_PHASES = ("investigating", "paused", "finishing")

    def __init__(self, runner, mode):
        self.runner = runner
        self.mode = mode
        self.commit = guard_commit()
        self.log = EventLog(mode, self.commit)
        self.task = None
        self.queue = None
        self._ctl = threading.Lock()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True,
                         name="ui-runner-loop").start()

    # ---- the three actions + reset ------------------------------------------

    def state(self):
        """GET /api/state: the event snapshot plus live truth and mailbox."""
        snap = self.log.snapshot()
        snap["truth"] = (reply_state(snap["email_id"])
                         if snap["email_id"] in MAILBOX else None)
        snap["mailbox"] = mailbox_summary(snap["email_id"])
        return snap

    def start_case(self, body):
        """POST /api/start: begin a run, one at a time (409 while running)."""
        email_id = body.get("email_id") or DEMO_CASES.get(
            str(body.get("case", "")).strip().upper())
        if email_id not in MAILBOX:
            return 400, {"error": f"Unknown case or email_id: {body}"}
        with self._ctl:
            if self.log.phase in self.RUNNING_PHASES:
                return 409, {"error": "A case is already running. "
                                      "Reset it first."}
            log = EventLog(self.mode, self.commit)
            self.log = log

            async def _go():
                """Run one case; failures become run_error events, with the
                traceback kept for the evidence log, never the console."""
                self.queue = asyncio.Queue()
                try:
                    await self.runner(email_id, log, self.queue.get)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    log.error(f"{type(exc).__name__}: {exc}",
                              traceback.format_exc())

            def _spawn():
                self.task = self.loop.create_task(_go())

            self.loop.call_soon_threadsafe(_spawn)
        return 200, {"started": email_id}

    def decide(self, body):
        """POST /api/decision: hand approve/reject to the paused run's queue
        (409 unless a pause is actually waiting on it)."""
        decision = str(body.get("decision", "")).strip().lower()
        reason = body.get("reason")
        if decision not in ("approve", "reject"):
            return 400, {"error": "decision must be 'approve' or 'reject'"}
        with self._ctl:
            if self.log.phase != "paused" or self.queue is None:
                return 409, {"error": "No approval is pending."}
            self.loop.call_soon_threadsafe(self.queue.put_nowait,
                                           (decision, reason))
        return 200, {"decided": decision}

    def reset(self):
        """POST /api/reset: cancel the run (3 s grace), reset_world(), and
        start a fresh EventLog — the clean slate between demo cases."""
        with self._ctl:
            task = self.task

            def _cancel():
                if task is not None and not task.done():
                    task.cancel()

            self.loop.call_soon_threadsafe(_cancel)
            deadline = time.monotonic() + 3.0
            while task is not None and not task.done() \
                    and time.monotonic() < deadline:
                time.sleep(0.02)
            if task is not None and not task.done():
                return 500, {"error": "The run did not stop within 3 s. "
                                      "Restart the server."}
            self.task, self.queue = None, None
            reset_world()
            self.log = EventLog(self.mode, self.commit)
        return 200, {"reset": True}


def make_handler(app):
    """A BaseHTTPRequestHandler subclass bound to one App via the closure."""
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status, payload):
            """Send payload as a JSON response; no-store keeps polls fresh."""
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _html(self, text):
            """Send the page (or the placeholder) as HTML, also no-store."""
            data = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _body(self):
            """The request body as a dict: {} when empty, None on bad JSON."""
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            try:
                return json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return None

        def do_GET(self):
            """Routes: / and /index.html (the page), /api/state."""
            if self.path.split("?")[0] in ("/", "/index.html"):
                if INDEX_PATH.exists():
                    self._html(INDEX_PATH.read_text(encoding="utf-8"))
                else:
                    self._html(PLACEHOLDER)
            elif self.path.split("?")[0] == "/api/state":
                self._json(200, app.state())
            else:
                self._json(404, {"error": f"No route: {self.path}"})

        def do_POST(self):
            """Routes: /api/start, /api/decision, /api/reset."""
            body = self._body()
            if body is None:
                self._json(400, {"error": "Body must be JSON."})
                return
            route = self.path.split("?")[0]
            if route == "/api/start":
                self._json(*app.start_case(body))
            elif route == "/api/decision":
                self._json(*app.decide(body))
            elif route == "/api/reset":
                self._json(*app.reset())
            else:
                self._json(404, {"error": f"No route: {self.path}"})

        def log_message(self, fmt, *args):  # keep the console readable
            pass

    return Handler


class UIServer(ThreadingHTTPServer):
    """ThreadingHTTPServer without SO_REUSEADDR. http.server turns reuse on
    by default, and on Windows that lets a second server bind 127.0.0.1:8765
    while the first is still alive — so a stale fake server could silently
    answer for a live one. With reuse off, the second start fails loudly."""
    allow_reuse_address = False


def make_server(app, port):
    """A UIServer on 127.0.0.1 only; port 0 (the offline checks) means
    an ephemeral port, read back from server.server_address."""
    return UIServer(("127.0.0.1", port), make_handler(app))


def main(argv=None):
    """Parse the flags, pick the fake or live runner, serve until Ctrl+C.

    Live mode refuses to start without a key in the environment or .env
    (rule 2: read through dotenv, never printed)."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fake", action="store_true",
                    help="use the canned fake runner: no model, no API key")
    ap.add_argument("--fake-delay", type=float, default=0.7,
                    help="seconds per fake step (default 0.7)")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args(argv)

    if args.fake:
        from ui.dev.fake_runner import make_fake_runner
        app = App(make_fake_runner(delay=args.fake_delay), mode="fake")
    else:
        from phishing_guard.config import has_openai_key
        if not has_openai_key():
            print("Live mode needs OPENAI_API_KEY in the environment or "
                  ".env (never printed). Add it, or run with --fake.")
            return 2
        from ui.live_runner import make_live_runner
        app = App(make_live_runner(), mode="live")
        print("LIVE mode: each run calls the OpenAI API.")

    server = make_server(app, args.port)
    host, port = server.server_address
    print(f"Phishing Guard UI server | mode {app.mode} | "
          f"commit {app.commit} | http://{host}:{port}/")
    if not INDEX_PATH.exists():
        print("ui/index.html not built yet (stage 2); serving a placeholder.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
