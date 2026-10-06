"""UI layer for the Phishing Guard demo (docs/ui-plan.md).

New files only; nothing in phishing_guard/ changes. Modules:
    events        EventLog, segment-to-event extraction, the pause loop
    fake_runner   canned segments shaped like the SDK's, for offline checks
    server        thin local HTTP server: start, decision, state, reset
    check_offline drives the server over HTTP with the fake runner, no API
"""
