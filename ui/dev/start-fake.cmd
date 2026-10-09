@echo off
rem Starts the Phishing Guard UI server in FAKE mode: canned data, no model,
rem no API key, no OpenAI calls. Double-click or run from any directory.
rem Uses the repo root's .venv after the cd, so it needs a checkout that
rem has one (the UI worktree does not; see PROGRESS.md).
cd /d "%~dp0..\.."
.venv\Scripts\python.exe ui\server.py --fake %*
pause
