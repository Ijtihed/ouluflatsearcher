from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class Listing(BaseModel):
    psoas_id: Optional[str] = None
    address: str = ""
    apartment_type: str = ""
    room_config: str = ""
    size_m2: Optional[float] = None
    rent_eur: Optional[float] = None
    leasing_start: Optional[str] = None
    leasing_end: Optional[str] = None
    description: str = ""
    contact_name: str = ""
    phone: str = ""
    email: str = ""
    posted_date: str = ""
    listing_url: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def listing_id(self) -> str:
        if self.psoas_id:
            return self.psoas_id
        raw = f"{self.address}|{self.apartment_type}|{self.rent_eur}|{self.leasing_start}|{self.leasing_end}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def telegram_message(self) -> str:
        lines = ["New PSOAS listing", ""]
        if self.address:
            lines.append(f"Address: {self.address}")
        if self.apartment_type:
            lines.append(f"Type: {self.apartment_type}")
        if self.room_config:
            lines[-1] += f" ({self.room_config})"
        if self.size_m2:
            lines.append(f"Size: {self.size_m2} m²")
        if self.rent_eur is not None:
            lines.append(f"Rent: {self.rent_eur:.0f} €/month")
        if self.leasing_start or self.leasing_end:
            start = self.leasing_start or "?"
            end = self.leasing_end or "?"
            lines.append(f"Leasing: {start} - {end}")
        if self.contact_name:
            lines.append(f"Contact: {self.contact_name}")
        if self.phone:
            lines.append(f"Phone: {self.phone}")
        if self.email:
            lines.append(f"Email: {self.email}")
        if self.description:
            desc = self.description[:300]
            if len(self.description) > 300:
                desc += "..."
            lines.append(f"\n{desc}")
        return "\n".join(lines)


class StoredListing(BaseModel):
    listing_id: str
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: str = ""
    notification_sent: bool = False
