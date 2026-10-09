# Phishing Guard & Coach

**Guard protects, Coach teaches, the human decides.**

An email security agent built on the OpenAI Agents SDK. Guard investigates a
suspicious email with real tools (a trained text classifier, threat
intelligence, the employee's profile), records a verdict, and asks the
employee for approval before moving anything. If the employee rejects the
move, Coach writes a short, personal lesson explaining the red flags — and
the case is escalated to security either way. The email's fate is always
decided by the mailbox state, never by the agent's words.

## Architecture

Two agents in a manager pattern: **Guard** (the manager) runs the whole
case, and **Coach** is exposed to Guard as a tool (`coach_user`, the SDK's
`as_tool` pattern), so Guard decides when a lesson is needed. Both agents
run on `gpt-5.4-mini`.

Guard has **nine tools in three layers**:

| Layer | Tools |
| --- | --- |
| Evidence | `classify_email_text` (the trained classifier), `check_sender_domain`, `check_url`, `get_user_profile` |
| Judgment | `record_verdict` (phishing / suspicious / legitimate, with red flags) |
| Action & follow-up | `move_to_phishing_folder`, `coach_user`, `log_training_event`, `escalate_to_security` |

The move tool is the **human-in-the-loop** step: it is declared with
`needs_approval=True`, so the run pauses and the employee approves or
rejects (with a reason) before anything is moved. A `check_move` input
guardrail additionally blocks a move before a verdict or on a legitimate
verdict. A rejected move leaves the email in the Inbox; the system state
(folder, training log, security queue) is the ground truth throughout.

## Setup

1. Python 3.14 (built on 3.14.8).
2. Create and activate a venv, then install:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. The key is read
   through python-dotenv and never printed.

## Data and classifier

The text classifier is trained on the Kaggle **Phishing Email Dataset** by
Naser Abdullah Alam. Put the dataset's CSVs in `data/` — the classifier
reads the combined `data/phishing_email.csv`. Run `01_train_classifier.ipynb`
to rebuild `phish_clf.joblib` (TF-IDF + logistic regression; training takes
about two minutes). On the held-out 20% (16,416 rows), the phishing class
scores precision 0.984, recall 0.987, F1 0.985, ROC-AUC 0.999.

The simulated world (10 + 20 emails, threat intel, three employees) lives
in `data/emails.json`, `data/threat_intel.json`, and `data/test_cases.json`;
`scripts/check_world.py` validates it without any model calls.

## Run the notebook demo

Open `02_guard_and_coach.ipynb`. Sections 1–6 build the agents and tools;
section 7 **Demo** has interactive cells for demo cases A (approve path),
B (reject path with coaching), and C (legitimate) — you type approve or
reject at the pause. Sections 8–10 hold the evaluation harness, results,
and findings; set `RUN_LIVE = False` to load the saved `results/latest.json`
instead of calling the API.

## Run Harbor Mail (the UI)

A simulated email client with the agent wired in:

- `ui\start-live.cmd` — live mode, each run calls the OpenAI API (needs
  the key in `.env`).
- `ui\dev\start-fake.cmd` — offline demo mode with canned scenarios, no
  API key needed.

Then open http://127.0.0.1:8765/. The header switches between **Outlook**
and **Gmail** client styles (same state, two looks). The Guard panel shows
the investigation as it streams — checks, judgment, the approval pause,
coaching, follow-up, and Guard's verbatim reply — with the raw event log
behind "Show the engine" and the authoritative mailbox state pinned below.

## Run the evaluation

```
.venv\Scripts\python.exe scripts\tuesday_check.py
```

Runs the 30 test cases with the reply judge, prints the averages, the
per-group table, and agent-versus-classifier, and saves rows and summaries
under `results/`. Useful flags: `--cases C-02 C-03`, `--tag mytag`,
`--no-judge`, `--no-save`.

## Repo layout

```
phishing_guard/        the package: tools, agents, runners, evaluation, judges
  classifier.py        TF-IDF + logistic regression over the Kaggle data
  tools.py             the nine tools and the check_move guardrail
  guard_agents.py      Guard and Coach instructions and builders
  runners.py           run_investigation, run_interactive, run_case
  evaluation.py        score_case, the metrics, summaries, baselines
  judge.py             the reply-faithfulness judge (reason-first)
  lesson_judge.py      the lesson-quality judge
  world.py             USERS, MAILBOX, threat intel, reset_world
data/                  emails, threat intel, test cases, Kaggle CSVs
scripts/               offline tests and the check scripts (tuesday_check.py)
ui/                    Harbor Mail: server.py, index.html, start scripts
results/               saved evaluation runs and FINAL_SUMMARY.md
01_train_classifier.ipynb   trains and saves phish_clf.joblib
02_guard_and_coach.ipynb    the build, demo, and evaluation notebook
docs/, design/         project brief, UI plan, mockup
```

## Evaluation design

- **30 cases**: C-01 to C-10 are the development set (tuning used their
  failures only); C-11 to C-30 are the exam set, written and blind-reviewed
  afterwards. 10 clear_phish, 10 clear_legit, 10 borderline; human
  decisions 10 approve, 10 reject, 10 not asked; 4 training simulations.
  Both answer keys were blind-reviewed and locked before any scoring.
- **10 metrics across three scopes**: from the tool trace —
  workflow_adherence, tool_correctness, argument_correctness,
  step_efficiency; from the end-of-run system state — verdict_correct,
  task_completion, and the flag metrics (precision, recall, F1 against the
  true labels); from the final reply — reply_faithful.
- **The LLM judge**: reply_faithful is scored by a separate judge agent
  that compares Guard's final reply with the actual folder, training log,
  and security queue. The judge went through three wordings; the final
  reason-first judge agreed 12/12 with hand labels, 6/6 on a blind
  hand-labelled round chosen by case ID before any judge answer was seen,
  and caught 3/3 planted false action claims. A separate lesson judge
  agreed with hand labels on 39 of 40 boxes over the 10 reject-case
  lessons (the hand labels themselves pass 38 of 40).
- **pass^3**: a case passes a run only if verdict_correct,
  workflow_adherence, task_completion, and reply_faithful all pass; pass^3
  is the share of cases that pass all three final runs.

## Final results

Guard frozen at tag `guard-final`, three full 30-case passes, 0 errors and
0 judge errors. Baseline = the pre-tuning run re-judged with the same
(third) judge. Full detail in `results/FINAL_SUMMARY.md`.

| Metric | baseline | pass1 | pass2 | pass3 | mean | range |
| --- | --- | --- | --- | --- | --- | --- |
| verdict_correct | 0.93 | 1.00 | 0.83 | 0.97 | 0.93 | 0.83-1.00 |
| workflow_adherence | 0.83 | 1.00 | 1.00 | 0.87 | 0.96 | 0.87-1.00 |
| task_completion | 0.77 | 1.00 | 0.83 | 0.83 | 0.89 | 0.83-1.00 |
| tool_correctness | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | - |
| argument_correctness | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | - |
| step_efficiency | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | - |
| flag precision | 0.75 | 0.75 | 0.82 | 0.79 | 0.79 | 0.75-0.82 |
| flag recall | 1.00 | 1.00 | 0.93 | 1.00 | 0.98 | 0.93-1.00 |
| flag F1 | 0.86 | 0.86 | 0.87 | 0.88 | 0.87 | 0.86-0.88 |
| reply_faithful (judge) | 0.73 | 1.00 | 1.00 | 1.00 | 1.00 | 90/90 replies |
| mean tool calls | 6.3 | 6.7 | 6.3 | 6.2 | 6.4 | - |

**pass^3 = 22/30 = 0.73** (per-run pass shares 30/30, 25/30, 25/30). By
group: clear_phish 9/10, clear_legit 9/10, borderline 4/10.

Classifier alone on the same 30 emails (subject + body, 0.5 threshold):
precision 0.90, recall 0.60, F1 0.72, ROC-AUC 0.91. The agent trades
precision for recall: recall 0.98 versus the classifier's 0.60, at the
cost of flagging borderline legitimate mail.

## Tuning log

One change at a time, chosen from dev-set (C-01 to C-10) failures only,
each verified on a full 30-case run with the same judge:

1. **Fix 1** — FOLLOW UP must complete before the reply (Guard had replied
   after an approved move without logging it).
2. **Fix 2** — the reply must copy Coach's lesson exactly, not summarize
   it (one run kept only 49% of the lesson's words).
3. **Attempt 1a (reverted)** — folding escalation into the approve
   sentence fixed the targeted skip but made Guard stop right after the
   move in 5 of 10 approve cases; completion 0.77 → 0.73.
4. **Fix 3 (kept, commit 2d2303d)** — the approve branch as an ordered
   sequence (log, then escalate if suspicious, only then reply); the
   reject branch ends with an explicit escalate. Adherence 0.83 → 0.97,
   completion 0.77 → 0.87.
5. **Fix 4 (kept, commit fd75429)** — a rejected move leaves the email in
   the Inbox and the reply must not claim it was moved. Rejected-move
   contradictions 3 → 0 on the 10 reject cases.

Net effect, single-run baseline → three-pass means: adherence 0.83 → 0.96,
completion 0.77 → 0.89, reply_faithful 0.73 → 1.00, with verdict accuracy
and the flag metrics unchanged within run-to-run noise.

## Known limits

- **Borderline verdict flapping** (6 of the 8 failing pass^3 cases): the
  same email gets 'suspicious' in one pass and 'legitimate' in another
  with no instruction change; C-29 is wrong in 2 of 3 passes. The DECIDE
  stage was not tuned.
- **Residual escalation skip, 2 of 90 runs** (C-10, C-27 in pass3): on
  suspicious + approve, Guard moved and logged but did not escalate —
  reduced from 4/30 in the baseline by fix 3, not eliminated.
- **Verdict recorded but no move offered, 2 of 90 runs** (C-12, C-30 in
  pass3): Guard replied without ever calling the move tool, so the
  employee was never asked.
- **Flag precision has a ceiling below 1.0 by design**: the locked answer
  key expects 'suspicious' on borderline truly-legitimate cases, and flag
  precision scores flags against true labels — in pass1 Guard matched the
  key on all 30 verdicts and precision was still 0.75.
- **Judge evidence is partial**: the 12/12 hand-label agreement includes
  cases that were in view during judge revision; the independent evidence
  is the 6/6 blind round and the 3/3 planted-error check. The judge also
  shows a recurring misreading that recording a verdict implies a
  training-log entry.
- The `check_move` guardrail runs after approval, as a backstop before
  execution; no run so far has exercised it, because Guard always recorded
  a verdict before moving.

## Team

Gabriel Gutierrez, Marina Gitelman, Jessy Salgado Palma, Tadrib Choudhury,
Darryl Jeune.
