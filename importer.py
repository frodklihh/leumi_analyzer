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

    # Last table contains transaction data
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
    """Parse Leumi bank statement exported as .xlsx.
    
    Dynamically locates the header row since Leumi exports include 
    metadata rows at the top of the file.
    """
    import pandas as pd

    # Step 1: Find which row contains the actual table headers
    df_raw = pd.read_excel(path, header=None)
    header_row_idx = 4  # Default fallback row

    for idx, row in df_raw.iterrows():
        row_str = " ".join(str(v) for v in row.values)
        if "תאריך" in row_str and ("יתרה" in row_str or "חובה" in row_str):
            header_row_idx = idx
            break

    # Step 2: Reload the file with the correct header row
    df = pd.read_excel(path, header=header_row_idx)
    df.columns = [str(c).strip() for c in df.columns]

    # Map typical Hebrew column names used by Bank Leumi
    date_col = next((c for c in df.columns if "תאריך" in c), df.columns[0])
    desc_col = next((c for c in df.columns if "תיאור" in c), df.columns[2] if len(df.columns) > 2 else df.columns[1])
    ref_col = next((c for c in df.columns if "אסמכתא" in c), None)
    debit_col = next((c for c in df.columns if "חובה" in c), None)
    credit_col = next((c for c in df.columns if "זכות" in c), None)
    balance_col = next((c for c in df.columns if "יתרה" in c), None)

    transactions = []
    for _, row in df.iterrows():
        try:
            date_raw = row[date_col]
            if pd.isna(date_raw) or str(date_raw).strip() == "" or "תאריך" in str(date_raw):
                continue

            if isinstance(date_raw, datetime):
                date = date_raw
            else:
                date = pd.to_datetime(date_raw, dayfirst=True).to_pydatetime()

            description = str(row[desc_col]).strip() if desc_col in row and not pd.isna(row[desc_col]) else ""
            if not description or description.lower() == "nan":
                continue

            reference = str(row[ref_col]).strip() if ref_col and ref_col in row and not pd.isna(row[ref_col]) else ""
            debit = _parse_amount(row[debit_col]) if debit_col and debit_col in row else 0.0
            credit = _parse_amount(row[credit_col]) if credit_col and credit_col in row else 0.0
            balance = _parse_amount(row[balance_col]) if balance_col and balance_col in row else 0.0

            transactions.append(Transaction(
                date=date.replace(tzinfo=None),
                description=description,
                reference=reference,
                debit=debit,
                credit=credit,
                balance=balance,
                source="bank",
            ))
        except Exception:
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
        # Peek at first rows to detect format
        df = pd.read_excel(path, header=None, nrows=5)
        all_text = " ".join(str(v) for row in df.itertuples(index=False) for v in row)

        # Bank statements contain these markers anywhere in the header area
        bank_markers = ["יתרה", "חובה", "תנועות בחשבון", "מסגרת האשראי"]
        if any(m in all_text for m in bank_markers):
            return parse_leumi_bank_xlsx(path)
        else:
            return parse_leumi_credit_card(path)

    return parse_leumi_xls(path)