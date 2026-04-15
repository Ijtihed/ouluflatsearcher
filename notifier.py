from __future__ import annotations

import logging

import requests

import config

log = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram(text: str) -> bool:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        log.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False

    url = TELEGRAM_API.format(token=config.TELEGRAM_BOT_TOKEN)
    try:
        resp = requests.post(
            url,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if resp.ok:
            log.info("Telegram message sent")
            return True
        log.error("Telegram API error %d: %s", resp.status_code, resp.text)
        return False
    except requests.RequestException:
        log.exception("Failed to send Telegram message")
        return False


def test_telegram() -> bool:
    return send_telegram("PSOAS Flat Searcher bot is working!")
