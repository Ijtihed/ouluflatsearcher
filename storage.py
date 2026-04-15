from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone

import config
from models import Listing

log = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(config.DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            listing_id       TEXT PRIMARY KEY,
            first_seen_at    TEXT NOT NULL,
            last_seen_at     TEXT NOT NULL,
            raw_data         TEXT NOT NULL,
            notification_sent INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def get_seen_ids() -> set[str]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT listing_id FROM listings").fetchall()
        return {r[0] for r in rows}
    finally:
        conn.close()


def save_listing(listing: Listing, notified: bool = False) -> None:
    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    raw = listing.model_dump_json()
    try:
        conn.execute(
            """
            INSERT INTO listings (listing_id, first_seen_at, last_seen_at, raw_data, notification_sent)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(listing_id) DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                raw_data = excluded.raw_data,
                notification_sent = CASE
                    WHEN excluded.notification_sent = 1 THEN 1
                    ELSE listings.notification_sent
                END
            """,
            (listing.listing_id, now, now, raw, int(notified)),
        )
        conn.commit()
    finally:
        conn.close()


def mark_notified(listing_id: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "UPDATE listings SET notification_sent = 1 WHERE listing_id = ?",
            (listing_id,),
        )
        conn.commit()
    finally:
        conn.close()


def export_csv(path: str) -> int:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT listing_id, first_seen_at, last_seen_at, raw_data, notification_sent FROM listings"
        ).fetchall()
    finally:
        conn.close()

    import csv

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["listing_id", "first_seen_at", "last_seen_at", "address", "type", "rent", "leasing", "contact", "notified"])
        for row in rows:
            data = json.loads(row[3])
            leasing = f"{data.get('leasing_start', '')} – {data.get('leasing_end', '')}"
            writer.writerow([
                row[0],
                row[1],
                row[2],
                data.get("address", ""),
                data.get("apartment_type", ""),
                data.get("rent_eur", ""),
                leasing,
                data.get("contact_name", ""),
                bool(row[4]),
            ])
    return len(rows)
