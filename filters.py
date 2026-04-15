from __future__ import annotations

import logging

import config
from models import Listing

log = logging.getLogger(__name__)


def is_relevant(listing: Listing) -> bool:
    if not _type_ok(listing):
        log.debug("Rejected %s: type '%s'", listing.address, listing.apartment_type)
        return False
    if not _rent_ok(listing):
        log.debug("Rejected %s: rent %.0f", listing.address, listing.rent_eur or 0)
        return False
    return True


def _type_ok(listing: Listing) -> bool:
    t = listing.apartment_type.lower()
    return any(allowed in t for allowed in config.ALLOWED_TYPES)


def _rent_ok(listing: Listing) -> bool:
    if listing.rent_eur is None:
        return True
    return listing.rent_eur <= config.MAX_RENT


def filter_listings(listings: list[Listing]) -> list[Listing]:
    relevant = [l for l in listings if is_relevant(l)]
    log.info("Filtered %d -> %d relevant listings", len(listings), len(relevant))
    return relevant
