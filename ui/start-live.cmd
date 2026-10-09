@echo off
rem Starts the Phishing Guard UI server in LIVE mode: every run calls the
rem real Guard on the OpenAI API. The key is read from .env by the server
rem and never printed. Double-click or run from any directory, then open
rem http://127.0.0.1:8765/ in the browser.
cd /d "%~dp0.."
"C:\Users\Gabriel Gutierrez\Documents\Projects\Phishing-Guard-ClaudeCode\.venv\Scripts\python.exe" ui\server.py %*
pause
