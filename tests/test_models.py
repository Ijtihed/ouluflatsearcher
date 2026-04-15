from __future__ import annotations

from models import Listing


def test_listing_id_from_psoas_id():
    l = Listing(psoas_id="ap_ilmoitus__12345", address="Test 1")
    assert l.listing_id == "ap_ilmoitus__12345"


def test_listing_id_hash_fallback():
    l = Listing(address="Test 1", apartment_type="Studio", rent_eur=400)
    assert len(l.listing_id) == 16
    assert l.listing_id.isalnum()


def test_listing_id_deterministic():
    a = Listing(address="Test 1", apartment_type="Studio", rent_eur=400)
    b = Listing(address="Test 1", apartment_type="Studio", rent_eur=400)
    assert a.listing_id == b.listing_id


def test_listing_id_different_for_different_data():
    a = Listing(address="Test 1", apartment_type="Studio", rent_eur=400)
    b = Listing(address="Test 2", apartment_type="Studio", rent_eur=400)
    assert a.listing_id != b.listing_id


def test_telegram_message_contains_address():
    l = Listing(address="Kandintie 3 D 14", apartment_type="Studio", rent_eur=375)
    msg = l.telegram_message()
    assert "Kandintie 3 D 14" in msg
    assert "375" in msg
    assert "Studio" in msg
