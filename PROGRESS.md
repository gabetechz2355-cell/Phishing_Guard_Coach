# Progress

## Done

- 2026-10-04: Project setup. `git init`, `.gitignore`, `.env` (empty key), `.env.example`, `CLAUDE.md`, `.venv` on Python 3.14.8 with `openai-agents==0.22.0`, `python-dotenv`, `scikit-learn`, `pandas`, `joblib`, `jupyter`, `ipykernel`.

- 2026-10-04: Sunday step 1, classifier. `phishing_guard/` package skeleton (`config.py`, `classifier.py`), thin `01_train_classifier.ipynb`, executed in place. Saved `phish_clf.joblib` and six held-out rows to `data/kaggle_holdout.json`. Held-out 20% (16,416 rows), phishing class: precision 0.984, recall 0.987, F1 0.985, ROC-AUC 0.999. Confusion matrix tn 7706, fp 141, fn 112, tp 8457. Training took about two minutes.

- 2026-10-04: Sunday step 2, world data. `phishing_guard/world.py` (USERS, loaders, `reset_world`), `data/emails.json` (10 emails E-001 to E-010, incl. demo A = E-001, B = E-002, C = E-003), `data/threat_intel.json` (13 domains, 5 URLs; `greenvalley-produce.example`, `mailbox-pay.example`, and the Green Valley catalog URL are deliberately unknown), `data/test_cases.json` (C-01 to C-10: 4 clear_phish, 3 clear_legit, 3 borderline; 3 approve, 4 reject, 3 not asked; 2 simulations). `scripts/check_world.py` validates shape, threat-intel coverage, and HITL-table consistency. These 10 are the development set the report must name.

- 2026-10-04: Sunday step 3, tools and Guard. `phishing_guard/tools.py` (four evidence tools + `record_verdict`, PLAN.md code verbatim except `record_verdict` now returns an error string for an unknown email instead of raising KeyError), `phishing_guard/guard_agents.py` (`GUARD_INSTRUCTIONS` verbatim, `make_guard(tools, extra)`, `build_input` verbatim, plus a Sunday-only addendum telling Guard the ACT/FOLLOW UP tools do not exist yet), `phishing_guard/trace_utils.py` (`show_trace` from the tutorial). `scripts/test_tools_offline.py` invokes each tool through the SDK's `on_invoke_tool` path with no model: 14/14 checks pass. Classifier alone on the 10 dev emails at 0.5: flags E-001, E-002, E-006, E-010; misses E-004 (payroll diversion, 0.20) and E-005 (gift cards, 0.39); clears all legit ones. That gap is the case for the agent.

## Next

- Sunday, Oct 4 checklist from PLAN.md: verify SDK pause/resume behavior; end-of-day check on three emails.

## Problems

- Git is installed at `C:\Program Files\Git\cmd` but was not on PATH in the Claude Code shell, so git is called by full path in this session. A new terminal should pick it up.
- Python is 3.14.8 from the Microsoft Store. All packages installed with wheels, so no issue so far. Note it if a dependency later refuses 3.14.
- Windows Smart App Control is on (enforce mode). On 2026-10-04 it blocked scipy's `_uarray.cp314-win_amd64.pyd` on first load, which made `import sklearn` fail once. A retry a minute later succeeded after the cloud reputation check, and a TF-IDF fit ran. If another `ImportError: DLL load failed ... Application Control policy has blocked this file` appears, especially inside Jupyter, wait a minute and retry before changing anything. Check `Microsoft-Windows-CodeIntegrity/Operational` event IDs 3077 and 3118 to see which file was blocked.
