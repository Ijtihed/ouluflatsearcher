from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

import config

log = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(config.RETRY_ATTEMPTS),
    wait=wait_fixed(config.RETRY_WAIT),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    reraise=True,
)
def fetch_page() -> str:
    log.info("Fetching %s", config.PSOAS_URL)
    resp = requests.get(
        config.PSOAS_URL,
        headers={"User-Agent": config.USER_AGENT},
        timeout=config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    log.info("Fetched %d bytes", len(resp.text))
    return resp.text


def save_snapshot(html: str, reason: str = "error") -> Path:
    config.SNAPSHOTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = config.SNAPSHOTS_DIR / f"{reason}_{ts}.html"
    path.write_text(html, encoding="utf-8")
    log.info("Saved HTML snapshot to %s", path)
    return path
