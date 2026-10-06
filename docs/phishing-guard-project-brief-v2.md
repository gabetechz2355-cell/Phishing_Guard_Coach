# Phishing Guard and Coach: project brief v2

Status as of Tuesday, October 6, 2026, mid-afternoon. The team meeting is at 6:30 PM today. The class presentation is Oct 10 (15 minutes plus 3 for questions, live demo of two cases, every member presents). Submission is Oct 12 (zip with a PDF report and the code).

## What this is

ISM6422 (Business AI Applications, FIU) team assignment: an agentic application on the OpenAI Agents SDK with at least two agents, at least two tools with one needing a human in the loop, and an evaluation at three scopes (end-to-end, trajectory, component) on at least 30 cases.

Our project: an email arrives in a mock inbox. Guard (the main agent) investigates it with tools it chooses, records a verdict (legitimate, suspicious, or phishing), and asks the employee before moving it. If the employee rejects the warning, Coach (a second agent, called by Guard as a tool) teaches them on that exact email. Everything is fictional (company Harbor Foods, domains ending in .example).

## Design

- Three layers: evidence (tools), judgment (Guard's verdict), action (gated by a human).
- Manager pattern: Guard calls Coach as a tool and control returns. We did not use handoffs.
- Nine tools: classify_email_text, check_sender_domain, check_url, get_user_profile, record_verdict, move_to_phishing_folder (needs approval, with a check_move guardrail), coach_user, log_training_event, escalate_to_security.
- Model gpt-5.4-mini, openai-agents==0.22.0, Python 3.14.8 on Windows.
- Classifier: TF-IDF plus logistic regression on the Kaggle Phishing Email Dataset (Naser Abdullah Alam, CC BY-SA 4.0). Held-out 20% is 16,416 emails, so training was about 65,700 and the cleaned dataset about 82,000. Held-out phishing-class precision 0.984, recall 0.987, F1 0.985, ROC-AUC 0.999.
- Test set: 30 cases, 10 clear phishing, 10 clear legitimate, 10 borderline. 24 are synthetic emails we wrote. 6 are held-out Kaggle rows with synthetic sender addresses and no links. The first 10 (C-01 to C-10) are the development set. The answer key was reviewed blind and locked (commit 71ab686).

## Evaluation: ten metrics

End-to-end: verdict accuracy, flag precision/recall/F1, lesson quality (LLM judge, not built yet), reply faithfulness (LLM judge). Trajectory: workflow adherence, task completion, step efficiency. Component: tool correctness, argument correctness, classifier alone.

## 30-case baseline (before tuning, Oct 6)

- Verdict accuracy 0.93, workflow adherence 0.83, task completion 0.77, tool, argument and step metrics 1.00 each.
- Flag precision 0.75, recall 1.00, F1 0.86. Classifier alone: precision 0.90, recall 0.60, F1 0.72.
- Reply faithfulness: 0.53 with the original judge, 0.60 with a second judge, 0.73 with the third judge (reason first, strict rule).
- Reading: Guard's judgment is strong and it catches every phishing email, but it often skips follow-up steps and writes replies that misstate what happened.

## Reply judge validation

Strict rule: a reply that says an action happened and then says it was rejected counts as a contradiction. Offered, proposed, attempted, or tried do not assert that the action happened. Agreement with our 12 human labels: original 7 of 12, second 9 of 12, third 12 of 12. The 12 are not an independent test because the judge was revised against them, and five were partly exposed to judge answers before labeling. Next: hand-label six fresh cases chosen by ID before seeing any judge answer (C-09, C-18, C-23, C-25, C-26, C-29), with no judge output on the sheet.

## Findings so far

- Skipped follow-through in 5 of 30 cases (escalation missed on suspicious plus approve: C-10, C-25, C-27, C-30; C-23 stopped before the move).
- Replies claim a move that did not happen (4 of the 12 hand-checked replies).
- Coach never sees the original email, so a lesson named a vendor the email never mentioned (C-18).
- Real email with mangled Kaggle text flagged suspicious (C-18), as we did in our own first pass.
- Guard once misspelled a vendor domain and passed the typo to Coach.

## Decisions

- C-01 required_tools does not include get_user_profile.
- Guard's instructions are frozen until after the 6:30 meeting. The demo version is git tag meeting-demo-oct6 (commit 0de0bec).
- Tuning comes after: fix the reply wording and the skipped escalation one change at a time, rerunning all 30 each time, tuning only on the first 10 cases.
- Use the third-judge numbers (0.73) as the reference for reply faithfulness.

## Still to do

Tuning round with before and after, lesson judge, three-pass run (pass^3), fresh judge check, README and a clean notebook run, report PDF, slides final, backup demo recording, zip and submit. Optional: a live front end, a Jev comparison row.

## Demo

Notebook 02_guard_and_coach.ipynb, section 7. Case A (E-001, fake password-expiry notice to Priya): type approve. Case B (E-002, bank-detail change to Dana from a lookalike vendor domain, a training simulation): type reject, then "That's Apex, we pay them every month." Run Run All Above Selected Cell on the Case A email cell, then run each email cell and demo cell in order. Rehearsed and working.

## UI plan (not started)

Goal: a real interface that runs the same Guard and Coach. Design is done as a mockup (Outlook-style and Gmail-style skins, Guard side panel in a red, silver and charcoal palette, a "Mailbox truth" strip read from system state, and a "Show the engine" panel). Build on a separate git branch so the frozen demo stays safe. Approach: a small local web server exposing start, decide, and read-state actions on the existing runners, one HTML page, and a recorded replay mode as a fallback. Plan with Claude Code first. Choose dependencies carefully: Windows Smart App Control can block newly installed compiled packages on first use. A published claude.ai artifact cannot call local code, so the live version must run from a local file or local server.

## Artifacts

- Build tracker: https://claude.ai/artifact/XUAFiAZf9e5c9daQiiFngU
- Interface mockup, Outlook and Gmail styles: https://claude.ai/artifact/HpafP2ynjUoaGG2jX35tTW
- Presentation deck, 17 slides: https://claude.ai/artifact/CqZvWYZRidG7psvpZcUvz2
- Prompt playbook: https://claude.ai/artifact/XmBD3T8es5gg5z7YRcW5Ux
- Architecture explainer: https://claude.ai/artifact/9YZkoWsGdn5bmnVgEdFtjr
- Demo walkthrough: https://claude.ai/artifact/2b6zHbHjEj9kUsgCj8KnSE
- Presentation script (Doc): https://claude.ai/code/artifact/2e5c25ca-da3c-43d4-8a6f-b3003f5539cd
- Implementation plan (Doc): https://claude.ai/code/artifact/36ba8fb8-203b-438e-862e-b82328f0165b

## Working rules

- Plan before code, one stage at a time, offline tests before spending money.
- Never edit the answer key or the scorer to raise a score. The key is locked.
- Never print or open .env.
- Coding agents commit by explicit path, never with a bulk commit.
- Explain decisions at the methodology level, in plain language.
