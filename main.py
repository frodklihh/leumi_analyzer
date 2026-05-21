import argparse
from pathlib import Path

from importer import load_file
from services import (
    categorize,
    combined_summary,
    filter_transactions,
    print_unknown_transactions,
    save_html_report,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "bank_file",
        help="Leumi bank statement (.xls)"
    )

    parser.add_argument(
        "card_file",
        help="Credit card detailed transactions (.xlsx)"
    )

    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)

    args = parser.parse_args()

    bank_path = Path(args.bank_file)
    card_path = Path(args.card_file)

    print(f"\n📂 Reading bank file: {bank_path.name}")
    bank_transactions = load_file(bank_path)

    print(f"✅ Loaded {len(bank_transactions)} bank transactions")

    print(f"\n📂 Reading card file: {card_path.name}")
    card_transactions = load_file(card_path)

    print(f"✅ Loaded {len(card_transactions)} card transactions")

    print("\n🏷️ Categorizing card transactions...")
    card_transactions = categorize(card_transactions)

    bank_transactions = filter_transactions(
        bank_transactions,
        year=args.year,
        month=args.month,
    )

    card_transactions = filter_transactions(
        card_transactions,
        year=args.year,
        month=args.month,
    )

    combined_summary(bank_transactions, card_transactions)
    print_unknown_transactions(card_transactions)
    save_html_report(bank_transactions, card_transactions)


if __name__ == "__main__":
    main()