"""Offline consistency checks for the mock world. No model calls.

Run:  .venv\\Scripts\\python.exe scripts\\check_world.py
Exits non-zero if any check fails.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phishing_guard.world import (MAILBOX, TEST_CASES, THREAT_INTEL, USERS,
                                  reset_world)

# Domains and URLs that are meant to have no threat-intel row.
DELIBERATELY_UNKNOWN_DOMAINS = {"greenvalley-produce.example", "mailbox-pay.example"}
DELIBERATELY_UNKNOWN_URLS = {"https://greenvalley-produce.example/catalog"}

EVIDENCE_WITH_LINKS = "check_url"
VERDICTS = {"legitimate", "suspicious", "phishing"}
CATEGORIES = {"clear_phish", "clear_legit", "borderline"}

problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


reset_world()

# Every email has the right shape and points at a real user.
for eid, e in MAILBOX.items():
    for key in ("to_user", "from_name", "from_addr", "reply_to", "subject",
                "body", "links", "folder", "is_simulation"):
        check(key in e, f"{eid}: missing field {key}")
    check(e["to_user"] in USERS, f"{eid}: unknown user {e['to_user']}")
    check(e["folder"] == "Inbox", f"{eid}: should start in Inbox")
    check(e["from_addr"].endswith(".example"), f"{eid}: non-.example From domain")
    for link in e["links"]:
        check(link in e["body"], f"{eid}: link {link} not present in body")
        check(".example" in link, f"{eid}: non-.example link {link}")

    # Threat intel coverage: a row, or deliberately none.
    domain = e["from_addr"].split("@")[-1].lower()
    check(domain in THREAT_INTEL["domains"] or domain in DELIBERATELY_UNKNOWN_DOMAINS,
          f"{eid}: From domain {domain} has no threat-intel row and is not listed as deliberately unknown")
    for link in e["links"]:
        check(link in THREAT_INTEL["urls"] or link in DELIBERATELY_UNKNOWN_URLS,
              f"{eid}: link {link} has no threat-intel row and is not listed as deliberately unknown")

# Every email has exactly one test case, and every test case points at an email.
case_emails = [c["email_id"] for c in TEST_CASES.values()]
check(len(case_emails) == len(set(case_emails)), "duplicate email_id across test cases")
check(set(case_emails) == set(MAILBOX), f"emails without cases or cases without emails: "
      f"{set(MAILBOX) ^ set(case_emails)}")

for cid, c in TEST_CASES.items():
    e = MAILBOX.get(c["email_id"])
    if e is None:
        continue
    check(c["category"] in CATEGORIES, f"{cid}: bad category {c['category']}")
    check(c["true_label"] in {"phishing", "legitimate"}, f"{cid}: bad true_label")
    check(c["expected_verdict"] in VERDICTS, f"{cid}: bad expected_verdict")
    check(c["user_decision"] in {"approve", "reject", None}, f"{cid}: bad user_decision")
    # The HITL table: a legitimate verdict means the employee is not asked.
    if c["expected_verdict"] == "legitimate":
        check(c["user_decision"] is None, f"{cid}: legitimate verdict but a scripted decision")
        check(c["red_flags"] == [], f"{cid}: legitimate verdict but red flags listed")
    else:
        check(c["user_decision"] in {"approve", "reject"}, f"{cid}: flagged verdict needs a decision")
        check(len(c["red_flags"]) > 0, f"{cid}: flagged verdict needs red flags")
    if c["user_decision"] == "reject":
        check(bool(c["user_reason"]), f"{cid}: reject needs a user_reason")
    # Tool expectations must match whether the email has links.
    if e["links"]:
        check(EVIDENCE_WITH_LINKS in c["required_tools"], f"{cid}: has links but check_url not required")
        check(EVIDENCE_WITH_LINKS not in c["forbidden_tools"], f"{cid}: has links but check_url forbidden")
    else:
        check(EVIDENCE_WITH_LINKS in c["forbidden_tools"], f"{cid}: no links but check_url not forbidden")
    check(not set(c["required_tools"]) & set(c["forbidden_tools"]), f"{cid}: tool both required and forbidden")

# Group counts for the development set.
from collections import Counter
cats = Counter(c["category"] for c in TEST_CASES.values())
decisions = Counter(str(c["user_decision"]) for c in TEST_CASES.values())
sims = sum(1 for e in MAILBOX.values() if e["is_simulation"])

print(f"emails: {len(MAILBOX)}  users: {len(USERS)}  domains: {len(THREAT_INTEL['domains'])}  urls: {len(THREAT_INTEL['urls'])}")
print(f"categories: {dict(cats)}")
print(f"decisions: {dict(decisions)}  simulations: {sims}")

if problems:
    print("\nPROBLEMS:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("\nworld OK")
