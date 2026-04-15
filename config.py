from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "listings.db"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"

PSOAS_URL = "https://www.psoas.fi/en/flat-exchange/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3
RETRY_WAIT = 5

DEFAULT_INTERVAL = 900  # 15 minutes

MAX_RENT = 500
ALLOWED_TYPES = ["studio", "family"]

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
