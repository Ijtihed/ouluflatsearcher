#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import time
import sys

import config
from filters import filter_listings
from notifier import send_telegram, test_telegram
from parser import parse_listings
from scraper import fetch_page, save_snapshot
from storage import get_seen_ids, save_listing, mark_notified, export_csv
from utils import setup_logging, console, print_listings_table

log = logging.getLogger(__name__)


def run_once(dry_run: bool = False, notify: bool = True) -> None:
    try:
        html = fetch_page()
    except Exception:
        log.exception("Failed to fetch PSOAS page")
        return

    listings = parse_listings(html)
    if not listings:
        log.warning("No listings parsed — HTML structure may have changed")
        save_snapshot(html, reason="no_listings")
        return

    relevant = filter_listings(listings)
    print_listings_table(relevant)

    if not notify:
        return

    seen_ids = get_seen_ids()
    new_listings = [l for l in relevant if l.listing_id not in seen_ids]

    if not new_listings:
        console.print(f"[dim]No new listings (all {len(relevant)} already seen)[/dim]")
    else:
        console.print(f"[bold green]{len(new_listings)} new listing(s)![/bold green]")

    for listing in relevant:
        if listing.listing_id in seen_ids:
            save_listing(listing, notified=False)
            continue

        save_listing(listing, notified=False)

        if dry_run:
            console.print(f"[yellow][DRY RUN][/yellow] Would notify: {listing.address}")
            console.print(listing.telegram_message())
            console.print()
        else:
            msg = listing.telegram_message()
            ok = send_telegram(msg)
            if ok:
                mark_notified(listing.listing_id)
                console.print(f"[green]Notified:[/green] {listing.address}")
            else:
                log.error("Failed to notify for %s", listing.address)


def watch(interval: int, dry_run: bool = False) -> None:
    console.print(f"[bold]Watching PSOAS every {interval}s (Ctrl+C to stop)[/bold]")
    while True:
        console.rule(f"[dim]{time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        try:
            run_once(dry_run=dry_run, notify=True)
        except KeyboardInterrupt:
            raise
        except Exception:
            log.exception("Error during watch cycle")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[bold]Stopped.[/bold]")
            break


def main() -> None:
    ap = argparse.ArgumentParser(description="PSOAS Flat Exchange monitor")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="Run once, show listings, notify new ones")
    mode.add_argument("--watch", action="store_true", help="Run in loop")
    mode.add_argument("--test-telegram", action="store_true", help="Send a test Telegram message")
    mode.add_argument("--export-csv", metavar="FILE", help="Export stored listings to CSV")

    ap.add_argument("--interval", type=int, default=config.DEFAULT_INTERVAL, help="Watch interval in seconds (default: 900)")
    ap.add_argument("--dry-run", action="store_true", help="Don't actually send Telegram messages")
    ap.add_argument("--verbose", "-v", action="store_true", help="Debug logging")

    args = ap.parse_args()
    setup_logging(verbose=args.verbose)

    if args.test_telegram:
        ok = test_telegram()
        sys.exit(0 if ok else 1)

    if args.export_csv:
        n = export_csv(args.export_csv)
        console.print(f"Exported {n} listings to {args.export_csv}")
        return

    if args.once:
        run_once(dry_run=args.dry_run)
    elif args.watch:
        watch(interval=args.interval, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
