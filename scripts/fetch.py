from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

from config.settings import email_config
from core.analytics import build_report
from core.period import billing_month
from fetcher import session
from fetcher.registry import BANK_REGISTRY, CARD_REGISTRY, make_bank_fetcher, make_card_fetcher
from leumi_analyzer.categorizer import categorize
from notifier.email import send_report
from scripts.importer import load_file
from views.console import print_report
from views.html import save_html_report

BASE_DIR = Path(__file__).resolve().parent.parent

_DEFAULT_BANK = "leumi"
_DEFAULT_CARDS = ["cal"]


def _resolve_period(year: int | None, month: int | None) -> tuple[int, int]:
    if year and month:
        return year, month
    current = billing_month(datetime.today())
    return current.year, current.month


async def _fetch_one(browser, fetcher, year: int, month: int, dest: Path) -> list[Path]:
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

    bank_name = args.bank
    card_names = args.cards

    print(f"\nPeriod : {year}-{month:02d}")
    print(f"Bank   : {bank_name}")
    print(f"Cards  : {', '.join(card_names)}")
    print(f"Output : {dest}\n")

    bank_fetcher = make_bank_fetcher(bank_name)
    card_fetchers = [make_card_fetcher(name) for name in card_names]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=args.headless)

        results = await asyncio.gather(
            _fetch_one(browser, bank_fetcher, year, month, dest),
            *[_fetch_one(browser, cf, year, month, dest) for cf in card_fetchers],
        )

        await browser.close()

    bank_files = results[0]
    card_files = [path for files in results[1:] for path in files]

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
    bank_choices = list(BANK_REGISTRY)
    card_choices = list(CARD_REGISTRY)

    parser = argparse.ArgumentParser(
        description="Auto-fetch bank + card statements and generate an HTML report."
    )
    parser.add_argument("--year",  type=int, help="Billing year  (default: current)")
    parser.add_argument("--month", type=int, help="Billing month (default: current)")
    parser.add_argument(
        "--bank",
        default=_DEFAULT_BANK,
        choices=bank_choices,
        help=f"Bank provider (default: {_DEFAULT_BANK})",
    )
    parser.add_argument(
        "--cards",
        nargs="+",
        default=_DEFAULT_CARDS,
        choices=card_choices,
        metavar="CARD",
        help=f"Card provider(s) (default: {_DEFAULT_CARDS}). Choices: {card_choices}",
    )
    parser.add_argument("--email",    action="store_true", help="Send report via email")
    parser.add_argument("--headless", action="store_true", help="Run browser without a visible window")
    parser.add_argument(
        "--clear-session",
        metavar="NAME",
        help="Delete the saved session for NAME and exit",
    )
    args = parser.parse_args()

    if args.clear_session:
        session.clear(args.clear_session)
        print(f"Session cleared: {args.clear_session}")
        return

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
