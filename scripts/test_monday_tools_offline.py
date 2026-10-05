"""Call the Monday tools and the check_move guardrail the way the SDK would,
with no model involved. Complements test_tools_offline.py (Sunday tools).

Run:  .venv/Scripts/python.exe scripts/test_monday_tools_offline.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.tool_context import ToolContext
from agents.tool_guardrails import ToolInputGuardrailData

from phishing_guard.tools import (check_move, escalate_to_security,
                                  log_training_event, move_to_phishing_folder,
                                  record_verdict)
from phishing_guard.world import MAILBOX, SECURITY_QUEUE, TRAINING_LOG, reset_world


def ctx_for(tool, **kwargs):
    args = json.dumps(kwargs)
    return ToolContext(context=None, tool_name=tool.name,
                       tool_call_id="call_test", tool_arguments=args), args


async def call(tool, **kwargs):
    """Invoke a FunctionTool through on_invoke_tool, as the runner does."""
    ctx, args = ctx_for(tool, **kwargs)
    return await tool.on_invoke_tool(ctx, args)


async def guard(**kwargs):
    """Run check_move on a proposed move_to_phishing_folder call."""
    ctx, _ = ctx_for(move_to_phishing_folder, **kwargs)
    out = await check_move.run(ToolInputGuardrailData(context=ctx, agent=None))
    return out.behavior["type"], out.behavior.get("message")


failures = []


def expect(label, cond, got):
    status = "ok " if cond else "FAIL"
    print(f"[{status}] {label}: {got}")
    if not cond:
        failures.append(label)


async def main():
    reset_world()

    # Guardrail: unknown email, no verdict, legitimate verdict, then allowed.
    r = await guard(email_id="E-999", reason="x")
    expect("check_move blocks unknown email", r[0] == "reject_content" and "unknown" in r[1], r)
    r = await guard(email_id="E-002", reason="x")
    expect("check_move blocks move before verdict", r[0] == "reject_content" and "record_verdict" in r[1], r)
    await call(record_verdict, email_id="E-003", verdict="legitimate", red_flags=[])
    r = await guard(email_id="E-003", reason="x")
    expect("check_move blocks move on legitimate verdict", r[0] == "reject_content" and "legitimate" in r[1], r)
    await call(record_verdict, email_id="E-002", verdict="phishing", red_flags=["lookalike sender domain"])
    r = await guard(email_id="E-002", reason="x")
    expect("check_move allows move on phishing verdict", r[0] == "allow", r)
    await call(record_verdict, email_id="E-009", verdict="suspicious", red_flags=["unknown domain"])
    r = await guard(email_id="E-009", reason="x")
    expect("check_move allows move on suspicious verdict", r[0] == "allow", r)

    # The move itself (the guardrail is enforced by the runner, not here).
    r = await call(move_to_phishing_folder, email_id="E-002", reason="Lookalike vendor domain asking to change bank details.")
    expect("move writes folder", MAILBOX["E-002"]["folder"] == "Phishing" and "moved" in r, r)
    r = await call(move_to_phishing_folder, email_id="E-999", reason="x")
    expect("move unknown email returns error, no raise", str(r).startswith("Error"), r)
    expect("move tool needs approval", move_to_phishing_folder.needs_approval is True,
           move_to_phishing_folder.needs_approval)

    # log_training_event: plain, simulation reveal, bad outcome, unknown email.
    r = await call(log_training_event, user_id="U-03", email_id="E-001", outcome="reported")
    expect("log plain email", r == "Logged." and TRAINING_LOG[-1] == {"user_id": "U-03", "email_id": "E-001", "outcome": "reported"}, r)
    r = await call(log_training_event, user_id="U-01", email_id="E-002", outcome="missed")
    expect("log simulation reveals", "training simulation" in r and TRAINING_LOG[-1]["outcome"] == "missed", r)
    r = await call(log_training_event, user_id="U-01", email_id="E-002", outcome="ignored")
    expect("log rejects bad outcome", str(r).startswith("Error") and len(TRAINING_LOG) == 2, r)
    r = await call(log_training_event, user_id="U-01", email_id="E-999", outcome="missed")
    expect("log unknown email returns error", str(r).startswith("Error") and len(TRAINING_LOG) == 2, r)

    # escalate_to_security: ticket numbering and unknown email.
    r = await call(escalate_to_security, email_id="E-002", summary="Lookalike of apexsupply.example; employee rejected.")
    expect("escalate first ticket", r == "Escalated as SEC-001." and SECURITY_QUEUE[0]["email_id"] == "E-002", r)
    r = await call(escalate_to_security, email_id="E-009", summary="Unknown first-contact vendor.")
    expect("escalate second ticket", r == "Escalated as SEC-002." and len(SECURITY_QUEUE) == 2, r)
    r = await call(escalate_to_security, email_id="E-999", summary="x")
    expect("escalate unknown email returns error", str(r).startswith("Error") and len(SECURITY_QUEUE) == 2, r)

    reset_world()
    expect("reset_world restores folder and empties logs",
           MAILBOX["E-002"]["folder"] == "Inbox" and not TRAINING_LOG and not SECURITY_QUEUE,
           (MAILBOX["E-002"]["folder"], len(TRAINING_LOG), len(SECURITY_QUEUE)))

    if failures:
        print("\nFAILED:", failures)
        sys.exit(1)
    print("\nMonday tools OK")


asyncio.run(main())
