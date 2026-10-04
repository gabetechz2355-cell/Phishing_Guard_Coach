"""Call each Sunday tool the way the SDK would, with no model involved.

Run:  .venv\\Scripts\\python.exe scripts\\test_tools_offline.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.tool_context import ToolContext

from phishing_guard.tools import (check_sender_domain, check_url,
                                  classify_email_text, get_user_profile,
                                  record_verdict)
from phishing_guard.world import MAILBOX, reset_world


async def call(tool, **kwargs):
    """Invoke a FunctionTool through on_invoke_tool, as the runner does."""
    args = json.dumps(kwargs)
    ctx = ToolContext(context=None, tool_name=tool.name,
                      tool_call_id="call_test", tool_arguments=args)
    out = await tool.on_invoke_tool(ctx, args)
    return out


failures = []


def expect(label, cond, got):
    status = "ok " if cond else "FAIL"
    print(f"[{status}] {label}: {got}")
    if not cond:
        failures.append(label)


async def main():
    reset_world()

    r = await call(classify_email_text, email_id="E-001")
    expect("classify E-001 (fake M365) scores high", r["phishing_probability"] >= 0.5, r)
    r = await call(classify_email_text, email_id="E-008")
    expect("classify E-008 (agenda) scores low", r["phishing_probability"] < 0.5, r)
    r = await call(classify_email_text, email_id="E-999")
    expect("classify unknown id returns error", "error" in r, r)

    r = await call(check_sender_domain, domain="apex-supp1y.example")
    expect("sender lookalike row", r.get("lookalike_of") == "apexsupply.example", r)
    r = await call(check_sender_domain, domain="  APEXSUPPLY.example ")
    expect("sender lookup is case/space tolerant", r.get("reputation") == "clean", r)
    r = await call(check_sender_domain, domain="greenvalley-produce.example")
    expect("sender unknown default", r == {"reputation": "unknown", "age_days": None, "lookalike_of": None}, r)

    r = await call(check_url, url="https://m365-secure-login.example/reset?u=priya.shah")
    expect("url blocklisted", r.get("on_blocklist") is True, r)
    r = await call(check_url, url="https://greenvalley-produce.example/catalog")
    expect("url unknown default", r == {"reputation": "unknown", "on_blocklist": False}, r)

    r = await call(get_user_profile, user_id="U-01")
    expect("profile U-01", r.get("role") == "Accounts Payable" and "apexsupply.example" in r["known_domains"], r)
    r = await call(get_user_profile, user_id="U-99")
    expect("profile unknown returns error", "error" in r, r)

    r = await call(record_verdict, email_id="E-002", verdict="phishing",
                   red_flags=["lookalike sender domain", "reply-to differs from sender"])
    expect("record_verdict writes to mailbox",
           MAILBOX["E-002"].get("verdict") == "phishing" and len(MAILBOX["E-002"]["red_flags"]) == 2, r)
    r = await call(record_verdict, email_id="E-002", verdict="maybe", red_flags=[])
    expect("record_verdict rejects bad verdict", str(r).startswith("Error"), r)
    r = await call(record_verdict, email_id="E-999", verdict="phishing", red_flags=[])
    expect("record_verdict unknown email returns error, no raise", str(r).startswith("Error"), r)

    reset_world()
    expect("reset_world clears verdict", "verdict" not in MAILBOX["E-002"], MAILBOX["E-002"].get("verdict"))

    # Classifier-alone view of the ten development emails, for the record.
    print("\nclassifier alone on the 10 dev emails (threshold 0.5):")
    for eid in sorted(MAILBOX):
        r = await call(classify_email_text, email_id=eid)
        print(f"  {eid}  p={r['phishing_probability']:.2f}  {r['top_words']}")

    if failures:
        print("\nFAILED:", failures)
        sys.exit(1)
    print("\ntools OK")


asyncio.run(main())
