# Phishing Guard UI — build plan

## Context

The agent and notebook demo are frozen at tag `meeting-demo-oct6` (0de0bec). This plan adds a real interface — one HTML page plus a thin local server — that runs the same Guard and Coach on E-001/E-002/E-003, in live and replay modes, judged by two clean rehearsals by Thursday evening Oct 8. The worktree is on branch `ui-demo`, which is the tag plus one commit (544f1cb, brief and mockup), so the required branch already exists. **Only new files are added; no existing file changes.** After approval, the first action is to write this plan to `docs/ui-plan.md` and commit it by explicit path with `C:\Program Files\Git\cmd\git.exe`.

---

## A. What I found by reading

**How a run starts.** `reset_world()` (`phishing_guard/world.py:55`) deep-copies `MAILBOX_ORIGINAL` back into `MAILBOX` and clears `TRAINING_LOG` and `SECURITY_QUEUE`. Then `Runner.run(guard, build_input(email_id), max_turns=12)` with `guard = make_guard_full()` (`guard_agents.py:108`, nine tools) and the input text from `build_input` (`guard_agents.py:122`). This is the pattern in every runner (`runners.py`).

**How it pauses.** When Guard calls `move_to_phishing_folder` (`needs_approval=True`, `tools.py:104`), the returned result has a non-empty `result.interruptions`. Each pending request carries `request.arguments`, a JSON string with `email_id` and `reason` (`runners.py:43-44`). The tool body has not run yet.

**How the decision gets back.** `state = result.to_state()`, then `state.approve(request)` or `state.reject(request, rejection_message="The employee rejected the move. Their reason: " + why)`, then `result = await Runner.run(guard, state)` to resume (`runners.py:41-55`; same pattern in the tutorial notebook, which covers exactly `Runner.run`, `interruptions`, `to_state`, `approve/reject` — no streaming, no hooks).

**Why neither existing runner can drive a web page directly.** `run_interactive` (`runners.py:33`) blocks on `input()` at the pause; `run_case` (`runners.py:61`) takes the decision from the test-case dict before the run starts. A browser decision arrives mid-run over HTTP. So the server needs one new async function (new file) that is `run_interactive`'s exact loop with `input()` replaced by `await` on an `asyncio.Queue` the decision endpoint feeds. It calls only `reset_world`, `build_input`, `Runner.run`, `to_state`, `approve`, `reject` — no Guard step is re-implemented, no instruction is copied. Flagging this per rule 1: it needs **no change to any existing file**.

**Where mailbox state lives.** Module-level `MAILBOX`, `TRAINING_LOG`, `SECURITY_QUEUE` in `world.py:52`. The truth strip is exactly `reply_state(email_id)` (`evaluation.py:95`): folder, training-log rows, security-queue rows for one email. `recorded_verdict` (`runners.py:82`) reads the verdict and red flags from `MAILBOX`.

**How it resets.** `reset_world()` — every runner calls it at the start of a case. Note: it resets **all** emails and both logs, so starting case B wipes case A's folder state. The sidebar folder counts therefore reflect only the current case; the mockup's accumulating counts across cases have no real source (departure noted in B).

**Reading tool calls from the trace.** `collect_calls` / `collect_call_ids` / `collect_outputs` (`evaluation.py:43-81`) walk `result.new_items` across segments and dedupe by `call_id`, because a resumed run repeats the pre-pause items (probe finding, PROGRESS Sunday step 4). The server reuses these three functions for event extraction — rule 11 (no duplicate steps) is solved by the same dedupe the notebook needed. A **rejected** move still yields a `tool_call_output_item` whose output is the rejection message, so "did the move run" must be read from `MAILBOX`, never from the trace (probe finding c) — the truth strip does exactly that.

**Key and model.** Importing `phishing_guard.config` loads `.env` via dotenv and sets the model; `has_openai_key()` checks without revealing. The server imports it and refuses to start live mode without a key. `.env` is never opened or printed.

**Not confirmed by reading** (named honestly):
1. Whether `Runner.run` works when driven from a background thread's event loop while a stdlib HTTP server handles requests on other threads. The notebook always ran it on the main loop. This is the plan's main technical unknown; it is checked by the first live run in stage 3, and everything before that is offline.
2. The exact attribute shape of an interruption beyond `request.arguments` (e.g. `raw_item.call_id`) — `probe_sdk.py` says `request.raw_item.call_id` matches the trace, and `monday_check` relies on it, so I treat it as confirmed secondhand.
3. Timing: PROGRESS says 30 cases took 300 s (≈10 s/case average) but demo cases with a pause run two segments; real per-segment wall time is unknown until the first timed run (the checklist sets the limit then).

---

## B. Source map: every mockup element → real source

| Mockup element | Real source | Gap / departure |
|---|---|---|
| "Design mockup" banner | Replaced by **mode badge**: `LIVE` or `REPLAY` + Guard commit (`git rev-parse --short HEAD` at server start; stored inside the recording for replay). Never cut. | New element, required by rule 8. |
| Skin toggle (Outlook/Gmail) | UI-local presentation state. No content. | — |
| Top bar name/role, "Signed in as" | `USERS[email.to_user]` via `MAILBOX` (system state, fixed template). | — |
| Inbox/Phishing folder counts | Count of `MAILBOX` folders, read each poll. | Resets when a new case starts (reset_world resets all emails). Mockup accumulated across cases — no real source for that. |
| Message list (3 rows, status line) | `MAILBOX` from/subject + server phase per case. | Status labels ("New", "Handled") are a fixed template over server phase. |
| Email pane (From, Reply-To, Subject, body) | The `MAILBOX` record, verbatim. | Mockup's A and C wording is illustrative; the real UI shows `data/emails.json` text (e.g. E-001's real subject is "Action required: your Harbor Foods password expires in 24 hours"). |
| Step cards: tool + result ("Read the text / Phishing probability 0.93…") | `tool_call`/`tool_result` events from `collect_calls`+`collect_outputs`. Title = fixed per-tool-name dict in code; detail line = fixed per-tool template over the tool's own JSON result. Unknown tool name → generic renderer (raw name, args, result), so any tool order or a new tool still renders (rule 6). | Mockup detail sentences are authored; the templates reproduce them from real result fields only. |
| "Skipped on purpose: no link check" | **No real source.** Guard emits no "skipped" event; asserting intent would be the UI making a judgment. | Recommend dropping it. A neutral alternative exists — a fixed template over system state: "This email has no links" from `MAILBOX[eid]["links"] == []`, shown without claiming intent. Open question I.2. |
| JUDGMENT card: verdict + red flags | `record_verdict` call arguments from the trace (equivalently `recorded_verdict()` from `MAILBOX`). | Mockup styles only phishing/legitimate; a `suspicious` style is added (silver badge in the existing palette) per rule 6. |
| APPROVAL card: "Guard wants to move…" + reason | Fixed template + `request.arguments["reason"]` — Guard's own words, like `runners.py:44` prints. | Mockup's prefilled input text ("I thought this was a real notice.") is authored → input starts empty; presenter types. |
| Approve / Reject buttons, reason input | UI → `POST /api/decision`. | — |
| ACTION card "Moved to the Phishing folder. Logged as reported." | Tool result strings verbatim ("E-001 moved to the Phishing folder.", "Logged.") rendered as events; the summary card becomes a fixed template over the truth state. | — |
| GUARD'S REPLY | `results[-1].final_output`, verbatim, always shown (rule 5) — including case B's known false "moved" claim next to a truth strip that contradicts it. | **Mockup omitted the reply on the reject path and admitted omitting the false sentence; the real UI must not.** Adds height — see layout. |
| COACH card: lesson | `coach_user` tool output via `collect_outputs` — Coach's words verbatim. | The reply also contains the lesson (Guard copies it), so the text appears twice. Open question I.3. |
| Simulation line | The `log_training_event` result string carries the reveal ("…was a training simulation…"); Guard's reply repeats it. Rendered from the tool result. | Mockup's standalone sentence is a styled rendering of that result, not authored text. |
| FOLLOW UP card ("stays in Inbox… SEC-001") | Fixed template over truth state + the `escalate_to_security` result ("Escalated as SEC-001."). | — |
| MAILBOX TRUTH strip | `reply_state(email_id)` equivalent, read directly from `MAILBOX`/`TRAINING_LOG`/`SECURITY_QUEUE` on every poll; recorded as `truth` events for replay. Never cut. | — |
| Show the engine panel | The same event list, rendered raw (name + args + result JSON, verbatim). One list, two renderings → steps match the engine one for one by construction. | Mockup fabricates engine lines in JS; real one renders actual events. Placement changes — see layout. |
| Footer disclaimer | Dropped. | — |

---

## C. The event format

One format for live and replay. The server keeps an append-only list of JSON events per run; `GET /api/state` returns `{mode, guard_commit, email_id, phase, events: [...], truth: {...}}`. A **replay file** is that same envelope with `recorded_at` added — a saved copy of what the server sent during a real live run, written automatically at the end of every live run to `recordings/`. Nobody writes one by hand; re-recording after tuning is one command (stage 5).

Event types: `case_started`, `tool_call` (call_id, name, args), `tool_result` (call_id, output), `approval_request` (call_id, args incl. Guard's reason), `decision` (approve/reject + typed reason), `truth` (folder, training_log, security_queue — snapshotted after each segment and after the decision), `reply` (final_output verbatim), `run_done`, `run_error` (message). `phase` (idle → investigating → paused → finishing → done / error) is derived from the last event, so replay derives it the same way.

Worked example, case B (abridged values):

```
{"seq":0,"type":"case_started","email_id":"E-002","mode":"live","guard_commit":"544f1cb","at":"2026-10-07T18:02:11"}
{"seq":1,"type":"tool_call","call_id":"c1","name":"classify_email_text","args":{"email_id":"E-002"}}
{"seq":2,"type":"tool_result","call_id":"c1","output":"{\"phishing_probability\": 0.75, \"top_words\": [...]}"}
{"seq":3,"type":"tool_call","call_id":"c2","name":"check_sender_domain","args":{"domain":"apex-supp1y.example"}}
{"seq":4,"type":"tool_result","call_id":"c2","output":"{\"reputation\": \"suspicious\", \"age_days\": 6, \"lookalike_of\": \"apexsupply.example\"}"}
{"seq":5,"type":"tool_call","call_id":"c3","name":"get_user_profile","args":{"user_id":"U-01"}}
{"seq":6,"type":"tool_result","call_id":"c3","output":"{\"role\": \"Accounts Payable\", ...}"}
{"seq":7,"type":"tool_call","call_id":"c4","name":"record_verdict","args":{"email_id":"E-002","verdict":"phishing","red_flags":["lookalike sender domain","reply-to differs from sender","bank detail change request"]}}
{"seq":8,"type":"tool_result","call_id":"c4","output":"Verdict recorded for E-002: phishing."}
{"seq":9,"type":"approval_request","call_id":"c5","args":{"email_id":"E-002","reason":"<Guard's one-sentence reason>"}}
{"seq":10,"type":"truth","folder":"Inbox","training_log":[],"security_queue":[]}
{"seq":11,"type":"decision","decision":"reject","reason":"That's Apex, we pay them every month."}
{"seq":12,"type":"tool_result","call_id":"c5","output":"The employee rejected the move. Their reason: That's Apex, we pay them every month."}
{"seq":13,"type":"tool_call","call_id":"c6","name":"coach_user","args":{"input":"..."}}
{"seq":14,"type":"tool_result","call_id":"c6","output":"1) Red flags: the sender domain is a lookalike... (the lesson, verbatim)"}
{"seq":15,"type":"tool_call","call_id":"c7","name":"log_training_event","args":{"user_id":"U-01","email_id":"E-002","outcome":"missed"}}
{"seq":16,"type":"tool_result","call_id":"c7","output":"Logged. This email was a training simulation sent by the security team. Tell the employee."}
{"seq":17,"type":"tool_call","call_id":"c8","name":"escalate_to_security","args":{"email_id":"E-002","summary":"..."}}
{"seq":18,"type":"tool_result","call_id":"c8","output":"Escalated as SEC-001."}
{"seq":19,"type":"reply","text":"<final_output verbatim, including any false 'moved' claim>"}
{"seq":20,"type":"truth","folder":"Inbox","training_log":[{"user_id":"U-01","email_id":"E-002","outcome":"missed"}],"security_queue":[{"email_id":"E-002","summary":"..."}]}
{"seq":21,"type":"run_done"}
```

Events 1–10 are extracted from segment 1 after it returns; 12–21 from segment 2, with segment 1's repeated items dropped by `call_id` (rule 11). Guard controls the order — the server records whatever happened.

## D. How steps appear as they happen

Three options considered:

1. **Per-segment extraction + polling (recommended).** The server appends events when each `Runner.run` segment returns; the page polls `/api/state` every 500 ms and reveals new step cards with a short stagger (as the mockup already animates). While segment 1 runs, the panel shows "Guard is investigating…" with an elapsed timer. Steps land in two honest bursts (evidence+verdict+pause, then follow-up+reply). Protects: stays entirely on the tutorial-covered API (CLAUDE.md: the tutorial is the source of truth), stdlib-only, and live/replay share the identical path (replay is just a pre-filled event list fed through the same poll). Costs: no mid-segment progress.
2. `Runner.run_streamed` + server-sent events: true per-tool timing, but an API surface the tutorial does not cover, a second transport to debug, and replay parity work. Rejected for risk on a frozen-demo week.
3. `RunHooks` (`on_tool_start/end`) appended in real time, still polling: middle ground, but also off-tutorial and it changes how the runner is called. Rejected for the same reason.

The engine panel timestamps events as extracted, so nothing is misrepresented: the stagger is pacing, not fabricated timing.

---

## E. Stages (each one sitting; stop for go-ahead between stages)

**Stage 0 — commit this plan.** Write `docs/ui-plan.md`, commit by explicit path. Check: `git log` shows it; working tree otherwise clean. Cost: $0.

**Stage 1 — event core + fake runner + server skeleton (~45 min).**
Build (all new files): `ui/events.py` (event builders; segment→events extraction reusing `collect_calls`/`collect_call_ids`/`collect_outputs`; truth snapshot via the `reply_state` pattern), `ui/fake_runner.py` (SimpleNamespace fake segments shaped like `scripts/test_score_offline.py:46-77` builds them, for A approve, B reject, C no-pause, plus an error case and an odd-order case), `ui/server.py` (stdlib `ThreadingHTTPServer` on 127.0.0.1 only; `POST /api/start`, `POST /api/decision`, `GET /api/state`, `POST /api/reset`; serves the static page; `--fake` flag swaps in the fake runner).
Check: `ui/check_offline.py` drives all fake cases over real HTTP and asserts event sequences, dedupe (no repeated call_ids), truth strips, and reset. Cost: $0.

**Stage 2 — the page (~90 min).**
Build: `ui/index.html` (one file, inline CSS/JS, no build step): both skins, all cards from section B, generic tool/verdict renderers, mode badge, truth strip, engine drawer, approve/reject + typed reason, stagger reveal, elapsed timer, error banner.
Check: server in `--fake` mode; click through A, B, C in the browser at 1280×720 (150 % zoom equivalent); case B's full post-reject state fits with no scrolling; engine panel matches step cards one for one. Cost: $0.

**Stage 3 — live runner (~30 min).**
Build: `ui/live_runner.py` — the `run_interactive` loop with `input()` replaced by `await queue.get()`; a background thread owns an asyncio loop; `/api/decision` posts into the queue; every live run auto-saves its event list to `recordings/live-<date>-<case>-<commit>.json`; `/api/reset` cancels the task and calls `reset_world()`. Guard commit read once at startup via the full git path.
Check: offline suite still passes with `--fake`; then, **with your go-ahead (API spend)**, one live run of case C — cheapest, no pause — proving the thread/loop unknown (A.1). Cost: ~1 case ≈ 8 model calls.

**Stage 4 — live A and B (~45 min).**
Run A (approve) and B (reject + typed reason) live once each, with your go-ahead; fix any rendering gap the real trace exposes (UI-side only). Keep the recordings. Cost: ~2–4 cases.

**Stage 5 — replay mode (~30 min).**
Build: `--replay <file>` / a replay picker listing `recordings/`; re-record = one command (`python ui/record.py E-002` = live run + auto-save, which stage 3 already does — this stage adds the paced playback through the same renderer and the mode badge swap). Commit frozen recordings by explicit path.
Check: replay stage-4 recordings offline; screen matches the live run; badge says REPLAY + commit. Cost: $0.

**Stage 6 — rehearsal prep (~40 min).**
One timed full pass (A, B, C) to set the per-case time limit; finalize the rehearsal checklist (below); 1920×1080 @150 % pass on the presentation machine; failure-handling polish. Then the two judged rehearsals are yours to run. Cost: timed pass 3 cases; rehearsals up to 9 cases.

Total build time ≈ 4 h 40 min against the 5 h budget.

## F. Cut order (truth strip and mode badge are never cut)

1. Gmail skin (keep Outlook only) — saves ~30 min in stage 2.
2. Engine drawer styling — fall back to the mockup's plain `<details><pre>` — saves ~15 min.
3. Stagger animation — steps appear in their honest bursts — saves ~10 min.
4. Stage 3's live case C — go straight to case A in stage 4 — saves one API run, not time.
5. Replay *picker* — hardcode `--replay <file>` on the command line. Replay mode itself is not cut: it is the fallback that protects the presentation.

## G. Failure handling (what the presenter sees, what they do)

- **API error / run raises:** the runner task catches the exception, appends `run_error`, phase becomes `error`; the page shows a red banner with the message and a "Reset case" button. Presenter: reset, retry once live; on a second failure, restart the server with `--replay` (manual switch, rule 8). The error text tells Guard-failures apart from UI-failures by rule: if the SDK raised, it's logged Guard/API-caused; if the record is clean but the screen broke, UI-caused.
- **Slow run:** the elapsed timer runs from `case_started`; the limit set in stage 6 is printed on the checklist. Past the limit the timer turns red — the presenter decides (finish or reset), nothing switches silently.
- **Stall mid-case (no new event, timer past limit):** same red-timer signal; Reset cancels the task, calls `reset_world()`, returns the case to clean. The partial recording is kept for the evidence log.
- **Server dead / page unreachable:** the notebook remains the guaranteed demo; the UI is shown as the bonus from a replay on a second attempt or not at all.

## H. Expected API cost

Everything in stages 0–2 and 5 is free (fake runner, replay). Live spend, in model calls on gpt-5.4-mini (a demo case ≈ 7–9 requests across two segments; Monday's whole check day was ≈ 50 calls; the 30-case baseline ≈ 300 s):

| What | Case runs | ≈ model calls |
|---|---|---|
| Stage 3 first live (C) | 1 | 8 |
| Stage 4 live A + B (+1 retry buffer) | 3 | 25 |
| Stage 6 timed pass (A, B, C) | 3 | 25 |
| Rehearsals, worst case 3 attempts × 3 cases | 9 | 75 |
| **Total worst case** | **16** | **≈ 130** |

Roughly half a 30-case baseline run; a few dollars at most on the mini model. Each live run is announced before it spends (CLAUDE.md rule).

## I. Risks and open questions, most serious first

1. **Threading unknown (A.1).** `Runner.run` on a background event loop behind a threaded stdlib server is unverified. Mitigation: it is the *first* live check (stage 3, one cheap case); if it misbehaves, fallback is a single-threaded server that blocks on the segment and a page that polls a file — same event format, decided then. This is the one place the plan could lose an hour.
2. **The "skipped on purpose" line.** No real source. My recommendation: drop it, optionally replacing it with the neutral, state-derived "This email has no links." **Your call.**
3. **Lesson appears twice on case B** — once as the Coach card (tool output) and once inside Guard's reply (rule 5 forbids trimming the reply). I recommend showing both in full; the two-column panel below is sized for it. If you prefer, the Coach card can collapse to a header after the reply renders — say so.
4. **Height check you asked for (rule 12).** The mockup's 400 px column cannot hold case B once the reply card is added: measured against the mockup's own type sizes, steps ≈ 156 px + judgment ≈ 120 + decision row ≈ 40 + lesson ≈ 170 + follow-up ≈ 55 + reply ≈ 240 + truth ≈ 56 + header ≈ 48 ≈ **885 px > 720**. Layout change: at presentation width the grid becomes **rail 200 px (folders + 3-message list merged) | email 380 px | Guard ≈ 700 px**, and the Guard panel flows its cards in **two internal columns** (steps/judgment/decision left ≈ 316 px; coach/follow-up/reply right ≈ 465 px), truth strip full-width at the panel's foot → tallest state ≈ 620 px, fits 720 with margin. The **engine panel opens as a drawer sliding over the email column**, so it never adds height. Departures from the mockup, stated: merged rail, two-column Guard panel, reply card on the reject path, suspicious-verdict style, engine drawer, mode badge replacing the mockup banner, folder counts resetting per case.
5. **Case B's reply contradicting the truth strip on stage.** Working as specified (rule 5, and the checklist says it does not fail the attempt), but the presenter should plan one sentence of narration for it; after the Guard-tuning merge it may disappear, and re-recording is one command.
6. **A second pause** (Guard retrying the move after a reject) has never been seen and is instruction-forbidden, but the loop allows 3 pauses — the UI renders any additional approval card generically rather than breaking.
7. **Rule 9 audit:** the server imports `world`, `guard_agents`, `runners`, `evaluation` helpers only; it never reads `test_cases.json` content, never writes `results/`, and `recordings/` is a new directory (committed). The decision comes from clicks, not the answer key.

---

## Rehearsal checklist (your draft, turned tickable and improved)

Header: attempt #, date/time, commit `git rev-parse --short HEAD` = ______, mode badge shows LIVE + same commit, per-case time limit = ______ (set in stage 6). Both clean rehearsals on the same commit, zero code changes between.

**Cold start**
- [ ] Server started fresh from a clean shell; page loaded fresh; no code edits or restarts after this point.
- [ ] Presentation resolution 1920×1080 at 150 % zoom; whole Guard panel visible, no scrollbars.
- [ ] Mode badge reads LIVE + the commit above; recordings folder is writable (auto-record on).

**Case A (E-001)**
- [ ] Verdict phishing; pause with Guard's reason shown; Approve clicked.
- [ ] Truth strip: Folder Phishing, training log `reported`, security queue empty.
- [ ] Guard's reply shown verbatim; finished inside the time limit.

**Case B (E-002)**
- [ ] Verdict phishing; pause; Reject; reason typed: "That's Apex, we pay them every month."
- [ ] Coach's lesson appears (tool output, verbatim); reply shown verbatim even if it misstates the move.
- [ ] Truth strip: Folder Inbox, log `missed`, security queue shows the SEC ticket.
- [ ] Simulation reveal visible; finished inside the time limit.

**Case C (E-003)**
- [ ] Verdict legitimate; no pause; no move; truth strip: Inbox, empty logs; inside the time limit.

**Cross-cutting**
- [ ] Engine panel opened once per case: steps on screen match engine events one for one, no duplicates, no missing step.
- [ ] Nothing on screen was typed or edited by hand; the reason input started empty.
- [ ] Recording file written for each case (named with date + commit).

**Scoring the attempt**
- [ ] Clean = every box above.
- [ ] Guard-caused failure (log separately, does **not** indict the UI): wrong verdict, or a follow-up step absent from the run record itself.
- [ ] UI-caused failure (fix + one-paragraph explanation before the next attempt): the record has a step the screen lacks, or the screen shows something the record lacks, or layout/scroll/crash.
- [ ] Explicitly not a failure: Guard's reply disagreeing with the truth strip, when both shown as they are.
- [ ] Two clean in a row, same commit, ≤3 attempts → UI is the main demo; else notebook is the demo, UI is the bonus (replay allowed).

---

## Verification summary

Offline: `ui/check_offline.py` (HTTP against the fake runner) after stages 1, 2, 5; browser click-through on fake data after stage 2. Live: one case C run (stage 3), A+B (stage 4), timed pass (stage 6) — each announced before spending. The notebook at the tag is untouched throughout; `git status` must show only added files at every commit.
