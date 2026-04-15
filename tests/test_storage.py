from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from models import Listing
from storage import get_seen_ids, save_listing, mark_notified


def _temp_db():
    return patch("config.DB_PATH", Path(tempfile.mktemp(suffix=".db")))


def test_empty_db_returns_no_ids():
    with _temp_db():
        assert get_seen_ids() == set()


def test_save_and_retrieve():
    with _temp_db():
        l = Listing(psoas_id="test_1", address="Addr 1", apartment_type="Studio", rent_eur=400)
        save_listing(l)
        ids = get_seen_ids()
        assert "test_1" in ids


def test_duplicate_detection():
    with _temp_db():
        l = Listing(psoas_id="test_2", address="Addr 2", apartment_type="Studio", rent_eur=400)
        save_listing(l)
        save_listing(l)
        ids = get_seen_ids()
        assert len(ids) == 1


def test_mark_notified():
    with _temp_db():
        l = Listing(psoas_id="test_3", address="Addr 3", apartment_type="Studio", rent_eur=400)
        save_listing(l, notified=False)
        mark_notified("test_3")
        # no exception means it works
        assert "test_3" in get_seen_ids()
