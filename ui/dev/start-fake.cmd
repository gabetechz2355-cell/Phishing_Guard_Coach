@echo off
rem Starts the Phishing Guard UI server in FAKE mode: canned data, no model,
rem no API key, no OpenAI calls. Double-click or run from any directory.
rem The worktree has no .venv of its own, so this uses the main checkout's
rem interpreter by full path (see PROGRESS.md and docs/ui-plan.md).
cd /d "%~dp0..\.."
"C:\Users\Gabriel Gutierrez\Documents\Projects\Phishing-Guard-ClaudeCode\.venv\Scripts\python.exe" ui\server.py --fake %*
pause
