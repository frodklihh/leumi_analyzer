from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

from config.settings import cal_credentials, email_config, leumi_credentials
from core.analytics import build_report
from core.period import billing_month
from fetcher import session
from fetcher.cal import CalCardFetcher
from fetcher.leumi import LeumiAccountFetcher
from leumi_analyzer.categorizer import categorize
from notifier.email import send_report
from scripts.importer import load_file
from views.console import print_report
from views.html import save_html_report

BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_period(year: int | None, month: int | None) -> tuple[int, int]:
    """Return (year, month) — defaults to the current billing month."""
    if year and month:
        return year, month
    current = billing_month(datetime.today())
    return current.year, current.month


async def _fetch_one(browser, fetcher, year: int, month: int, dest: Path) -> list[Path]:
    """Run a single fetcher in its own browser context."""
    ctx = await browser.new_context()
    await session.load(ctx, fetcher.name)
    try:
        return await fetcher.fetch(ctx, year, month, dest)
    except NotImplementedError as e:
        print(f"[{fetcher.name}] not yet implemented — skipping: {e}")
        return []
    finally:
        await session.save(ctx, fetcher.name)
        await ctx.close()


async def _run(args: argparse.Namespace) -> None:
    year, month = _resolve_period(args.year, args.month)
    dest = BASE_DIR / "reports" / f"{year}-{month:02d}"
    dest.mkdir(parents=True, exist_ok=True)

    print(f"\nPeriod : {year}-{month:02d}")
    print(f"Output : {dest}\n")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=args.headless)

        leumi = LeumiAccountFetcher(leumi_credentials())
        cal = CalCardFetcher(cal_credentials())

        bank_files, card_files = await asyncio.gather(
            _fetch_one(browser, leumi, year, month, dest),
            _fetch_one(browser, cal, year, month, dest),
        )

        await browser.close()

    if not bank_files and not card_files:
        print("No files downloaded — nothing to analyse.")
        return

    bank_txs = [tx for f in bank_files for tx in load_file(f)]
    card_txs = [tx for f in card_files for tx in load_file(f)]

    print(f"Bank transactions : {len(bank_txs)}")
    print(f"Card transactions : {len(card_txs)}\n")

    bank_txs = categorize(bank_txs)
    card_txs = categorize(card_txs)

    report = build_report(bank_txs, card_txs, year=year, month=month)
    html_path = dest / "report.html"

    print_report(report, card_txs)
    save_html_report(report, output_path=str(html_path))
    print(f"\nReport saved: {html_path}")

    if args.email:
        send_report(html_path, report, email_config())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto-fetch Leumi + Cal statements and generate an HTML report."
    )
    parser.add_argument("--year", type=int, help="Billing year  (default: current)")
    parser.add_argument("--month", type=int, help="Billing month (default: current)")
    parser.add_argument("--email", action="store_true", help="Send report via email after generation")
    parser.add_argument("--headless", action="store_true", help="Run browser without a visible window")
    parser.add_argument(
        "--clear-session",
        metavar="BANK",
        help="Delete the saved session for BANK and exit (leumi_bank | cal_card)",
    )
    args = parser.parse_args()

    if args.clear_session:
        session.clear(args.clear_session)
        print(f"Session cleared: {args.clear_session}")
        return

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
