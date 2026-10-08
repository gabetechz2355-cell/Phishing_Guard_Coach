# Final evaluation summary: Guard at tag guard-final, three passes

2026-10-07. Three full 30-case passes with the reason-first reply judge
(`final-pass1`, `final-pass2`, `final-pass3`), Guard frozen at tag
`guard-final` (tuning fixes 3 and 4 applied; commits 2d2303d and fd75429).
All three passes ran with 0 errors and 0 judge errors. The first pass3
attempt hit an OpenAI connection outage after C-11 (19 error rows); its
files were moved to `results/outage/` and left uncommitted, and pass3 was
rerun cleanly as `20261007-233143-final-pass3`.

Run files: `20261007-222717-final-pass1`, `20261007-223250-final-pass2`,
`20261007-233143-final-pass3` (.json, .csv, -vs-classifier.csv each).

## The 10 metrics per pass

Baseline = the pre-tuning 30-case run re-judged with the same (third) judge
(`20261006-113554-baseline-rejudged-reasonfirst`), single pass.

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

Classifier alone on the same 30 emails (subject + body, 0.5 threshold):
precision 0.90, recall 0.60, F1 0.72, ROC-AUC 0.91. The agent trades
precision for recall: it misses almost nothing the classifier misses
(recall 0.98 vs 0.60) at the cost of flagging borderline legitimate mail.

On the precision ceiling: the answer key expects 'suspicious' on borderline
truly-legitimate cases, and flag precision scores flags against true labels,
so key-correct behavior caps precision below 1.0. In pass1 Guard matched the
key on all 30 verdicts and precision was still 0.75.

## pass^3

A case passes a run only if verdict_correct, workflow_adherence,
task_completion, and reply_faithful all pass in that run. pass^3 is the
share of cases that pass all three runs.

**pass^3 = 22/30 = 0.73.** Per-run pass shares: 30/30, 25/30, 25/30.

| Group | pass^3 |
| --- | --- |
| clear_phish | 9/10 |
| clear_legit | 9/10 |
| borderline | 4/10 |

## The 8 failing cases

| Case | p1 p2 p3 | Run and cause |
| --- | --- | --- |
| C-10 | Y Y . | pass3: suspicious + approve, moved and logged but skipped escalation |
| C-12 | Y Y . | pass3: phishing verdict recorded, then no move offered at all |
| C-18 | Y . Y | pass2: verdict flap ('suspicious' on true legitimate) |
| C-23 | Y . Y | pass2: verdict flap ('legitimate', expected suspicious) |
| C-27 | Y . . | pass2: verdict flap; pass3: suspicious + approve, skipped escalation |
| C-28 | Y . Y | pass2: verdict flap ('legitimate', expected suspicious) |
| C-29 | Y . . | pass2 and pass3: verdict flap ('legitimate', expected suspicious) |
| C-30 | Y . . | pass3: suspicious verdict recorded, then no move offered at all |

## Three failure causes

1. **Borderline verdict flapping** (6 of the 8 failing cases; 6 wrong
   verdicts across the 90 case-runs, all borderline or C-18). The same email
   gets 'suspicious' in one pass and 'legitimate' in another with no
   instruction change. C-29 is the least stable (wrong in 2 of 3 passes).
   This lives in the DECIDE stage, which the tuning session did not touch.
2. **Residual escalation skip, 2 of 90** (C-10 and C-27, pass3 only): on
   suspicious + approve, Guard moved and logged but did not escalate. Tuning
   fix 3 cut this from 4/30 in the baseline to 2/90, reduced but not
   eliminated.
3. **Verdict recorded but no move offered, 2 of 90** (C-12 and C-30, pass3
   only): Guard recorded a phishing or suspicious verdict and replied without
   calling move_to_phishing_folder, so the employee was never asked. The
   baseline showed this once (C-23).

## Judge validation

reply_faithful is scored by the third (reason-first) judge. Its agreement
evidence, per `judge_check_6.md`: 6 of 6 on blind hand-labelled cases chosen
by ID before any judge answer was seen (all six labels CONSISTENT, so that
round measures false alarms only, and none occurred), on top of 12 of 12 on
the earlier, partly exposed hand check. Known intermittent false alarms from
tuning-run outputs are listed there; they would understate, not overstate,
faithfulness. The blind check found no false alarms. Because every reply in
it was faithful, it does not test whether the judge catches real
contradictions; that side is covered by the planted-error check in
`judge_check_planted.md`: three saved replies (C-09, C-18, C-29) each had
one false action sentence planted — a claimed move with the folder still
Inbox, a claimed "reported" log with the log outcome missed, and a claimed
escalation with the security queue empty — and the judge, run through the
same build_judge_input / parse path, labeled all three CONTRADICTS, 3 of 3,
each reason citing the matching state mismatch.

## Versus the baseline

The tuning session's two kept changes (ordered FOLLOW UP with per-branch
escalation; rejected-move wording) moved the single-run numbers from
adherence 0.83 / completion 0.77 / reply_faithful 0.73 to three-pass means
of 0.96 / 0.89 / 1.00, with verdict accuracy and the flag metrics unchanged
within the run-to-run noise of the borderline cases.
