from __future__ import annotations

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from models import Listing

log = logging.getLogger(__name__)

# ── Selectors (update these first if PSOAS changes their HTML) ──────────────
LISTING_CARD_CLASS = "card-ap-ilmoitus"
TITLE_CLASS = "card-ap-ilmoitus__title"
LEASING_CLASS = "card-ap-ilmoitus__ajankohta"
CONTACT_CLASS = "card-ap-ilmoitus__contact"
DIRECT_LINK_CLASS = "card-ap-ilmoitus__directlink"
RENT_SECTION_HEADER_ID = "postings"  # "Available For Rent" heading


def parse_listings(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "lxml")
    listings: list[Listing] = []

    rent_header = soup.find("h2", id=RENT_SECTION_HEADER_ID)
    if rent_header is None:
        rent_header = soup.find("h2", string=re.compile(r"Available\s+For\s+Rent", re.I))

    if rent_header is None:
        log.warning("Could not find 'Available For Rent' section header")
        cards = soup.find_all("div", class_=LISTING_CARD_CLASS)
    else:
        container = rent_header.find_next("div", class_=re.compile(r"ap_ilmoitukset"))
        if container:
            cards = container.find_all("div", class_=LISTING_CARD_CLASS)
        else:
            cards = rent_header.find_all_next("div", class_=LISTING_CARD_CLASS)

    log.info("Found %d listing cards", len(cards))

    for card in cards:
        try:
            listing = _parse_card(card)
            if listing:
                listings.append(listing)
        except Exception:
            log.exception("Failed to parse a listing card")

    return listings


def _parse_card(card: Tag) -> Optional[Listing]:
    psoas_id = card.get("id", "")
    if isinstance(psoas_id, list):
        psoas_id = psoas_id[0] if psoas_id else ""

    title_tag = card.find("b", class_=TITLE_CLASS)
    address = title_tag.get_text(strip=True) if title_tag else ""

    apartment_type, room_config, size_m2, rent_eur = "", "", None, None
    info_p = card.find("p")
    if info_p:
        apartment_type, room_config, size_m2, rent_eur = _parse_info_paragraph(info_p)

    leasing_start, leasing_end = None, None
    leasing_p = card.find("p", class_=LEASING_CLASS)
    if leasing_p:
        leasing_start, leasing_end = _parse_leasing(leasing_p.get_text())

    description = ""
    desc_candidates = card.find_all("p")
    for p in desc_candidates:
        classes = p.get("class", [])
        if any(c in classes for c in [LEASING_CLASS, CONTACT_CLASS]):
            continue
        text = p.get_text(strip=True)
        if text and text != info_p.get_text(strip=True) if info_p else True:
            if len(text) > 50:
                description = text
                break

    contact_name, phone, email = "", "", ""
    contact_p = card.find("p", class_=CONTACT_CLASS)
    if contact_p:
        contact_name, phone, email = _parse_contact(contact_p)

    posted_date, listing_url = "", ""
    link_tag = card.find("a", class_=DIRECT_LINK_CLASS)
    if link_tag:
        listing_url = link_tag.get("href", "")
        posted_date = link_tag.get_text(strip=True)

    return Listing(
        psoas_id=psoas_id or None,
        address=address,
        apartment_type=apartment_type,
        room_config=room_config,
        size_m2=size_m2,
        rent_eur=rent_eur,
        leasing_start=leasing_start,
        leasing_end=leasing_end,
        description=description,
        contact_name=contact_name,
        phone=phone,
        email=email,
        posted_date=posted_date,
        listing_url=listing_url,
    )


def _parse_info_paragraph(p: Tag) -> tuple[str, str, Optional[float], Optional[float]]:
    text = p.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    apartment_type = ""
    room_config = ""
    size_m2: Optional[float] = None
    rent_eur: Optional[float] = None

    for line in lines:
        if re.search(r"(studio|family|shared|solu|yksiö|perheasunto)", line, re.I):
            type_match = re.match(r"^(Studio|Family|Shared\s*apartment|Solu|Yksiö|Perheasunto)", line, re.I)
            if type_match:
                apartment_type = type_match.group(1).strip()

            config_match = re.search(r"-\s*(\d+H\s*\+\s*\w+)", line, re.I)
            if config_match:
                room_config = config_match.group(1).strip()

            size_match = re.search(r"(\d+[.,]?\d*)\s*m", line)
            if size_match:
                size_m2 = float(size_match.group(1).replace(",", "."))

        rent_match = re.search(r"(\d+[.,]?\d*)\s*€", line)
        if rent_match and "max" not in line.lower():
            rent_eur = float(rent_match.group(1).replace(",", "."))

    return apartment_type, room_config, size_m2, rent_eur


def _parse_leasing(text: str) -> tuple[Optional[str], Optional[str]]:
    dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", text)
    start = dates[0] if len(dates) >= 1 else None
    end = dates[1] if len(dates) >= 2 else None
    return start, end


def _parse_contact(p: Tag) -> tuple[str, str, str]:
    parts = [s.strip() for s in p.stripped_strings]
    name = parts[0] if parts else ""
    phone = ""
    email = ""
    for part in parts[1:]:
        if "@" in part:
            email = part
        elif re.search(r"[\d+]", part):
            phone = part
    return name, phone, email
