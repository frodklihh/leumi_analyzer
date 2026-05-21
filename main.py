"""
main.py - entry point
"""

import argparse
from pathlib import Path

from importer import load_file
from categorizer import categorize
from reporter import (
    combined_summary,
    filter_transactions,
    print_unknown_transactions,
    save_html_report,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Leumi bank + credit card statements"
    )
    parser.add_argument("bank_file", help="Bank statement (.xls or .xlsx)")
    parser.add_argument("card_file", help="Credit card transactions (.xlsx)")
    parser.add_argument("--year", type=int, help="Filter by billing year")
    parser.add_argument("--month", type=int, help="Filter by billing month")
    args = parser.parse_args()

    print(f"\n📂 Reading bank file: {Path(args.bank_file).name}")
    bank_transactions = load_file(args.bank_file)
    print(f"✅ Loaded {len(bank_transactions)} bank transactions")

    print(f"\n📂 Reading card file: {Path(args.card_file).name}")
    card_transactions = load_file(args.card_file)
    print(f"✅ Loaded {len(card_transactions)} card transactions")

    print("\n🏷️  Categorizing...")
    card_transactions = categorize(card_transactions)
    bank_transactions = categorize(bank_transactions)

    bank_transactions = filter_transactions(bank_transactions, year=args.year, month=args.month)
    card_transactions = filter_transactions(card_transactions, year=args.year, month=args.month)

    if not bank_transactions and not card_transactions:
        print("⚠️  No transactions found for the given filter.")
        return

    combined_summary(bank_transactions, card_transactions)
    print_unknown_transactions(card_transactions)
    save_html_report(
        bank_transactions,
        card_transactions,
        year=args.year,
        month=args.month,
    )


if __name__ == "__main__":
    main()