"""UI layer for the Phishing Guard demo (docs/ui-plan.md).

New files only; nothing in phishing_guard/ changes. Modules:
    events        EventLog, segment-to-event extraction, the pause loop
    server        thin local HTTP server: start, decision, state, reset
    dev/          fake runner and the offline check: dev-only, no API
"""
