# Progress

## Done

- 2026-10-04: Project setup. `git init`, `.gitignore`, `.env` (empty key), `.env.example`, `CLAUDE.md`, `.venv` on Python 3.14.8 with `openai-agents==0.22.0`, `python-dotenv`, `scikit-learn`, `pandas`, `joblib`, `jupyter`, `ipykernel`.

- 2026-10-04: Sunday step 1, classifier. `phishing_guard/` package skeleton (`config.py`, `classifier.py`), thin `01_train_classifier.ipynb`, executed in place. Saved `phish_clf.joblib` and six held-out rows to `data/kaggle_holdout.json`. Held-out 20% (16,416 rows), phishing class: precision 0.984, recall 0.987, F1 0.985, ROC-AUC 0.999. Confusion matrix tn 7706, fp 141, fn 112, tp 8457. Training took about two minutes.

## Next

- Sunday, Oct 4 checklist from PLAN.md: write personas, threat-intel table, and first 10 emails; build the four evidence tools and `record_verdict`; verify SDK pause/resume behavior; end-of-day check on three emails.

## Problems

- Git is installed at `C:\Program Files\Git\cmd` but was not on PATH in the Claude Code shell, so git is called by full path in this session. A new terminal should pick it up.
- Python is 3.14.8 from the Microsoft Store. All packages installed with wheels, so no issue so far. Note it if a dependency later refuses 3.14.
- Windows Smart App Control is on (enforce mode). On 2026-10-04 it blocked scipy's `_uarray.cp314-win_amd64.pyd` on first load, which made `import sklearn` fail once. A retry a minute later succeeded after the cloud reputation check, and a TF-IDF fit ran. If another `ImportError: DLL load failed ... Application Control policy has blocked this file` appears, especially inside Jupyter, wait a minute and retry before changing anything. Check `Microsoft-Windows-CodeIntegrity/Operational` event IDs 3077 and 3118 to see which file was blocked.
