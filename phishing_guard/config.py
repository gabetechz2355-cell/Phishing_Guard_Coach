"""Runtime configuration shared by every notebook and script.

The OpenAI key comes from the environment. python-dotenv reads .env first; if
the key is still missing or empty, ensure_openai_key() asks with getpass. The
key is never printed. Tracing is off, as in the tutorial setup cell.
"""

import os
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv
from agents import set_tracing_disabled

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_PATH = ROOT / "phish_clf.joblib"

# Reads ROOT/.env if present. An empty OPENAI_API_KEY= line sets the variable
# to "", which is falsy, so the getpass fallback below still triggers.
load_dotenv(ROOT / ".env")

lm_model = "gpt-5.4-mini"

set_tracing_disabled(True)


def ensure_openai_key() -> None:
    """Prompt for the key only when the environment does not already have one."""
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass("Enter your OPENAI API key: ")


def has_openai_key() -> bool:
    """True if a non-empty key is loaded. Never reveals the key itself."""
    return bool(os.environ.get("OPENAI_API_KEY"))
