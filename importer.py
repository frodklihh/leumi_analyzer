"""
importer.py - parser for Bank Leumi export files

Leumi exports:
- .xls  -> HTML tables (bank statement)
- .xlsx -> two formats: bank statement or credit card transactions
"""

import re
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import math


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


def _parse_amount(s) -> float:
    """Convert '₪5,403.92' or NaN to a float."""
    if s is None:
        return 0.0
    # Handle pandas/numpy NaN
    try:
        if isinstance(s, float) and math.isnan(s):
            return 0.0
    except (TypeError, ValueError):
        pass
    cleaned = str(s).replace("₪", "").replace(",", "").replace(" ", "").strip()
    if not cleaned or cleaned.lower() == "nan":
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_leumi_xls(path: str | Path) -> list[Transaction]:
    """Parse Leumi .xls (HTML) bank statement."""
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
            transactions.append(Transaction(
                date=date,
                description=cells[2],
                reference=cells[3],
                debit=_parse_amount(cells[4]),
                credit=_parse_amount(cells[5]),
                balance=_parse_amount(cells[6]),
                source="bank",
            ))
        except (ValueError, IndexError):
            continue

    return transactions


def parse_leumi_bank_xlsx(path: str | Path) -> list[Transaction]:
    """Parse Leumi bank statement in xlsx format.

    Column layout (header on row 1):
        0: balance, 1: debit, 2: nan, 3: credit, 4: nan, 5: description, 6: date
    """
    import pandas as pd

    df = pd.read_excel(path, header=1)
    transactions = []

    for _, row in df.iterrows():
        try:
            date_raw = row.iloc[6]
            description = str(row.iloc[5]).strip()
            debit_raw = row.iloc[1]
            credit_raw = row.iloc[3]
            balance_raw = row.iloc[0]

            if str(date_raw) == "nan" or description == "nan":
                continue

            date = pd.to_datetime(date_raw).to_pydatetime().replace(tzinfo=None)

            transactions.append(Transaction(
                date=date,
                description=description,
                reference="",
                debit=_parse_amount(debit_raw),
                credit=_parse_amount(credit_raw),
                balance=_parse_amount(balance_raw),
                source="bank",
            ))
        except (ValueError, TypeError):
            continue

    return transactions


def parse_leumi_credit_card(path: str | Path) -> list[Transaction]:
    """Parse Leumi credit card transactions xlsx.

    Column layout (header on row 1):
        0: date, 1: merchant name, 2: amount, 3: card, ...
    """
    import pandas as pd

    df = pd.read_excel(path, header=1)
    transactions = []

    for _, row in df.iterrows():
        try:
            date_raw = row.iloc[0]
            description = str(row.iloc[1]).strip()
            amount_raw = row.iloc[2]

            if str(date_raw) == "nan" or str(amount_raw) == "nan" or description == "nan":
                continue

            date = pd.to_datetime(date_raw).to_pydatetime().replace(tzinfo=None)
            amount = float(str(amount_raw).replace(",", ""))

            transactions.append(Transaction(
                date=date,
                description=description,
                reference="",
                debit=amount if amount > 0 else 0.0,
                credit=abs(amount) if amount < 0 else 0.0,
                balance=0.0,
                source="credit_card",
            ))
        except (ValueError, TypeError):
            continue

    return transactions


def load_file(path: str | Path) -> list[Transaction]:
    """Auto-detect file format and parse accordingly."""
    import pandas as pd

    path = Path(path)

    if path.suffix.lower() == ".xlsx":
        # Peek at row 1 to detect which xlsx format
        df = pd.read_excel(path, header=None, nrows=2)
        second_row = str(df.iloc[1, 0]) if len(df) > 1 else ""

        if "יתרה" in second_row or "חובה" in second_row:
            return parse_leumi_bank_xlsx(path)
        else:
            return parse_leumi_credit_card(path)

    return parse_leumi_xls(path)