"""
main.py - entry point
<<<<<<< HEAD

Usage:
    python main.py bank.xls card.xlsx
    python main.py bank.xls card1.xlsx card2.xlsx
    python main.py bank.xls card1.xlsx card2.xlsx --year 2026 --month 5
=======
>>>>>>> 4076023 (Add categorization and reporting modules; implement transaction parsing and HTML report generation)
"""

import argparse
from pathlib import Path

from importer import load_file
from categorizer import categorize
<<<<<<< HEAD
from core.analytics import build_report, filter_transactions
from views.console import print_report
from views.html import save_html_report
=======
from reporter import (
    combined_summary,
    filter_transactions,
    print_unknown_transactions,
    save_html_report,
)
>>>>>>> 4076023 (Add categorization and reporting modules; implement transaction parsing and HTML report generation)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Leumi bank + credit card statements"
    )
    parser.add_argument("bank_file", help="Bank statement (.xls or .xlsx)")
<<<<<<< HEAD
    parser.add_argument(
        "card_files",
        nargs="+",
        help="Credit card transactions (one or more .xlsx files)",
    )
    parser.add_argument("--year", type=int, help="Filter by billing year")
    parser.add_argument("--month", type=int, help="Filter by billing month")
    parser.add_argument("--output", default="reports/report.html", help="Output HTML path")
=======
    parser.add_argument("card_file", help="Credit card transactions (.xlsx)")
    parser.add_argument("--year", type=int, help="Filter by billing year")
    parser.add_argument("--month", type=int, help="Filter by billing month")
>>>>>>> 4076023 (Add categorization and reporting modules; implement transaction parsing and HTML report generation)
    args = parser.parse_args()

    print(f"\n📂 Reading bank file: {Path(args.bank_file).name}")
    bank_transactions = load_file(args.bank_file)
    print(f"✅ Loaded {len(bank_transactions)} bank transactions")

<<<<<<< HEAD
    card_transactions = []
    for card_file in args.card_files:
        print(f"\n📂 Reading card file: {Path(card_file).name}")
        txs = load_file(card_file)
        print(f"✅ Loaded {len(txs)} card transactions")
        card_transactions.extend(txs)

    print(f"\n📊 Total card transactions: {len(card_transactions)}")

    print("\n🏷️  Categorizing...")
    bank_transactions = categorize(bank_transactions)
=======
    print(f"\n📂 Reading card file: {Path(args.card_file).name}")
    card_transactions = load_file(args.card_file)
    print(f"✅ Loaded {len(card_transactions)} card transactions")

    print("\n🏷️  Categorizing...")
>>>>>>> 4076023 (Add categorization and reporting modules; implement transaction parsing and HTML report generation)
    card_transactions = categorize(card_transactions)
    bank_transactions = categorize(bank_transactions)

    bank_transactions = filter_transactions(bank_transactions, year=args.year, month=args.month)
    card_transactions = filter_transactions(card_transactions, year=args.year, month=args.month)

    if not bank_transactions and not card_transactions:
        print("⚠️  No transactions found for the given filter.")
        return

<<<<<<< HEAD
    report = build_report(
=======
    combined_summary(bank_transactions, card_transactions)
    print_unknown_transactions(card_transactions)
    save_html_report(
>>>>>>> 4076023 (Add categorization and reporting modules; implement transaction parsing and HTML report generation)
        bank_transactions,
        card_transactions,
        year=args.year,
        month=args.month,
    )

<<<<<<< HEAD
    print_report(report, card_transactions)
    save_html_report(report, output_path=args.output)

=======
>>>>>>> 4076023 (Add categorization and reporting modules; implement transaction parsing and HTML report generation)

if __name__ == "__main__":
    main()