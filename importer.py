# importer.py

"""
importer.py - parser for Bank Leumi export files

Leumi exports:
- .xls  -> HTML tables (bank statement)
- .xlsx -> detailed credit card transactions
"""

import re
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    date: datetime
    description: str
    reference: str
    debit: float
    credit: float
    balance: float
    source: str = ""
    category: str = ""


def _parse_amount(s: str) -> float:
    """Convert '5,403.92' to 5403.92"""
    return float(str(s).replace(",", "").strip() or "0")


def parse_leumi_xls(path: str | Path) -> list[Transaction]:
    """Parse Leumi .xls (HTML) export file."""
    from bs4 import BeautifulSoup

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        return []

    data_table = tables[-1]
    rows = data_table.find_all("tr")

    transactions = []

    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]

        if len(cells) < 7:
            continue

        if not re.match(r"\d{2}/\d{2}/\d{4}", cells[0]):
            continue

        try:
            date = datetime.strptime(cells[0], "%d/%m/%Y")

            transactions.append(
                Transaction(
                    date=date,
                    description=cells[2],
                    reference=cells[3],
                    debit=_parse_amount(cells[4]),
                    credit=_parse_amount(cells[5]),
                    balance=_parse_amount(cells[6]),
                    source="bank",
                )
            )

        except (ValueError, IndexError):
            continue

    return transactions


def parse_leumi_credit_card(path: str | Path) -> list[Transaction]:
    """Parse Leumi credit card transactions xlsx."""

    import pandas as pd

    df = pd.read_excel(path, header=1)

    transactions = []

    for _, row in df.iterrows():
        try:
            date_raw = row.iloc[0]
            description = str(row.iloc[1]).strip()
            amount_raw = row.iloc[2]

            if str(date_raw) == "nan":
                continue

            if str(amount_raw) == "nan":
                continue

            if description == "nan":
                continue

            date = pd.to_datetime(date_raw).to_pydatetime().replace(
                tzinfo=None
            )

            amount = float(str(amount_raw).replace(",", ""))

            transactions.append(
                Transaction(
                    date=date,
                    description=description,
                    reference="",
                    debit=amount if amount > 0 else 0.0,
                    credit=abs(amount) if amount < 0 else 0.0,
                    balance=0.0,
                    source="credit_card",
                )
            )

        except (ValueError, TypeError):
            continue

    return transactions


def load_file(path: str | Path) -> list[Transaction]:
    """Auto detect file format."""

    path = Path(path)

    if path.suffix.lower() == ".xlsx":
        return parse_leumi_credit_card(path)

    return parse_leumi_xls(path)