from __future__ import annotations

import logging
import sys

import io
import os

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from models import Listing

if os.name == "nt":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

console = Console(force_terminal=True)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def print_listings_table(listings: list[Listing]) -> None:
    if not listings:
        console.print("[yellow]No relevant listings found.[/yellow]")
        return

    table = Table(title="PSOAS Relevant Listings", show_lines=True)
    table.add_column("Address", style="cyan", min_width=20)
    table.add_column("Type", style="green")
    table.add_column("Size", justify="right")
    table.add_column("Rent", justify="right", style="bold yellow")
    table.add_column("Leasing", style="magenta")
    table.add_column("Contact", style="white")
    table.add_column("Posted", style="dim")

    for l in listings:
        size = f"{l.size_m2} m2" if l.size_m2 else "-"
        rent = f"{l.rent_eur:.0f} EUR" if l.rent_eur is not None else "-"
        leasing = ""
        if l.leasing_start or l.leasing_end:
            leasing = f"{l.leasing_start or '?'} - {l.leasing_end or '?'}"
        contact = l.contact_name
        if l.phone:
            contact += f"\n{l.phone}"

        table.add_row(l.address, l.apartment_type, size, rent, leasing, contact, l.posted_date)

    console.print(table)
