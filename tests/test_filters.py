from __future__ import annotations

from filters import is_relevant
from models import Listing


def _make(apt_type: str = "Studio", rent: float | None = 400) -> Listing:
    return Listing(address="Test 1 A 1", apartment_type=apt_type, rent_eur=rent)


def test_studio_under_500():
    assert is_relevant(_make("Studio", 400)) is True


def test_family_under_500():
    assert is_relevant(_make("Family", 450)) is True


def test_studio_at_500():
    assert is_relevant(_make("Studio", 500)) is True


def test_studio_over_500():
    assert is_relevant(_make("Studio", 501)) is False


def test_shared_rejected():
    assert is_relevant(_make("Shared apartment", 300)) is False


def test_unknown_type_rejected():
    assert is_relevant(_make("Loft", 300)) is False


def test_none_rent_accepted():
    assert is_relevant(_make("Studio", None)) is True


def test_family_case_insensitive():
    assert is_relevant(_make("family", 400)) is True
