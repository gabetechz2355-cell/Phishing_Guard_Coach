"""The mock world: users, mailbox, threat intel, and the two logs.

All state lives in five Python structures. reset_world() restores them before
every run so each case starts clean. TEST_CASES is the answer key; no tool
reads it, so the agents never see labels.
"""

import copy
import json

from .config import DATA_DIR

COMPANY_DOMAIN = "harborfoods.example"

USERS = {
    "U-01": {
        "user_id": "U-01",
        "name": "Dana Ruiz",
        "email": "dana.ruiz@harborfoods.example",
        "role": "Accounts Payable",
        "known_domains": ["apexsupply.example", "coastalfreight.example"],
        "past_misses": {"invoice_fraud": 1},
    },
    "U-02": {
        "user_id": "U-02",
        "name": "Marcus Lee",
        "email": "marcus.lee@harborfoods.example",
        "role": "HR Coordinator",
        "known_domains": ["brightpathbenefits.example", "paywell.example"],
        "past_misses": {},
    },
    "U-03": {
        "user_id": "U-03",
        "name": "Priya Shah",
        "email": "priya.shah@harborfoods.example",
        "role": "Regional Sales",
        "known_domains": ["metrodeli.example", "northstar-grocers.example",
                          "freshmarket-co.example"],
        "past_misses": {},
    },
}


def _load(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


MAILBOX_ORIGINAL = _load("emails.json")
THREAT_INTEL = _load("threat_intel.json")
TEST_CASES = _load("test_cases.json")

MAILBOX, TRAINING_LOG, SECURITY_QUEUE = {}, [], []


def reset_world():
    """Put every email back in the Inbox and empty both logs."""
    MAILBOX.clear()
    MAILBOX.update(copy.deepcopy(MAILBOX_ORIGINAL))
    TRAINING_LOG.clear()
    SECURITY_QUEUE.clear()


reset_world()
