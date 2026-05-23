"""
main.py - entry point
"""

import argparse
from pathlib import Path

from scripts.importer import load_file
from leumi_analyzer.categorizer import categorize
from core.analytics import build_report, filter_transactions
from views.console import print_report
from views.html import save_html_report


BASE_DIR = Path(__file__).resolve().parent.parent

# Making dynamic paths for templates and reports, so we can run the script from anywhere
TEMPLATE_DIR = BASE_DIR / "templates"
REPORT_DIR = BASE_DIR / "reports"

# Ensure the report directory exists
REPORT_DIR.mkdir(exist_ok=True)
template_path = TEMPLATE_DIR / "report.html"


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Leumi bank + credit card statements"
    )
    parser.add_argument("bank_file", help="Bank statement (.xls or .xlsx)")
    parser.add_argument(
        "card_files",
        nargs="+",
        help="Credit card transactions (one or more .xlsx files)",
    )
    parser.add_argument("--year", type=int, help="Filter by billing year")
    parser.add_argument("--month", type=int, help="Filter by billing month")
    parser.add_argument("--output", default="reports/report.html", help="Output HTML path")
    args = parser.parse_args()

    print(f"\n📂 Reading bank file: {Path(args.bank_file).name}")
    bank_transactions = load_file(args.bank_file)
    print(f"✅ Loaded {len(bank_transactions)} bank transactions")

    card_transactions = []
    for card_file in args.card_files:
        print(f"\n📂 Reading card file: {Path(card_file).name}")
        txs = load_file(card_file)
        print(f"✅ Loaded {len(txs)} card transactions")
        card_transactions.extend(txs)

    print(f"\n📊 Total card transactions: {len(card_transactions)}")

    print("\n🏷️  Categorizing...")
    bank_transactions = categorize(bank_transactions)
    card_transactions = categorize(card_transactions)

    report = build_report(
        bank_transactions,
        card_transactions,
        year=args.year,
        month=args.month,
    )

    if report.total_income == 0 and report.total_expenses == 0:
        print("⚠️  No transactions found for the given filter.")
        return

    print_report(report, card_transactions)
    save_html_report(report, output_path=args.output)


if __name__ == "__main__":
    main()