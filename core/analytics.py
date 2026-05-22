"""
core/analytics.py - pure data calculations and aggregations
"""

from collections import defaultdict
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime

from importer import Transaction
from core.period import billing_month


UNKNOWN_CATEGORY = "❓ Other"


@dataclass
class CategoryBreakdown:
    """Spending data for a single category."""
    name: str
    total: float
    transactions: list[Transaction] = field(default_factory=list)


@dataclass
class MonthlyBreakdown:
    """Aggregated data for one billing month."""
    year: int
    month: int
    label: str
    income: float
    expenses: float
    net: float
    categories: list[CategoryBreakdown] = field(default_factory=list)
    income_transactions: list[Transaction] = field(default_factory=list)

@dataclass
class ReportData:
    """All data needed to render a report."""
    period_label: str
    year: int | None
    month: int | None
    opening_balance: float
    closing_balance: float
    balance_change: float   # 👈 ADD THIS
    total_income: float
    total_expenses: float
    net: float
    categories: list[CategoryBreakdown]
    income_transactions: list[Transaction]
    monthly_breakdown: list[MonthlyBreakdown]


# ── Filtering ─────────────────────────────────────────────────────────────────

def filter_transactions(
    transactions: list[Transaction],
    year: int | None = None,
    month: int | None = None,
    cutoff_day: int = 16,
) -> list[Transaction]:
    """Filter by billing year/month (16th-to-15th cycle)."""
    result = transactions
    if year:
        result = [tx for tx in result if billing_month(tx.date, cutoff_day).year == year]
    if month:
        result = [tx for tx in result if billing_month(tx.date, cutoff_day).month == month]
    return result


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_card_payment(tx: Transaction) -> bool:
    """Detect bank transactions that are credit card payments."""
    desc = tx.description.lower()
    markers = ["ויזה", "כרטיסי אשראי", "ישראכרט", "max", "cal", "מקס", "כאל"]
    return any(m in desc for m in markers)


def combined_spending(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
) -> dict[str, list[Transaction]]:
    """Merge bank + card transactions by category, excluding card payments."""
    by_category: dict[str, list[Transaction]] = defaultdict(list)

    for tx in bank_transactions:
        if tx.debit > 0 and not _is_card_payment(tx):
            by_category[tx.category].append(tx)

    for tx in card_transactions:
        if tx.debit > 0:
            by_category[tx.category].append(tx)

    return by_category


def _compute_balances(bank_transactions: list[Transaction]) -> tuple[float, float]:
    """Compute opening and closing balance for the period."""
    if not bank_transactions:
        return 0.0, 0.0

    min_date = min(tx.date for tx in bank_transactions)
    max_date = max(tx.date for tx in bank_transactions)

    # On a single day, first transaction (by row order) has the HIGHEST balance,
    # since each subsequent transaction reduces it.
    first_day = [tx for tx in bank_transactions if tx.date == min_date]
    first_tx = min(first_day, key=lambda t: t.balance)
    opening = first_tx.balance

    # Closing = lowest balance on the last day (the last transaction of the day)
    last_day = [tx for tx in bank_transactions if tx.date == max_date]
    closing = min(last_day, key=lambda t: t.balance).balance

    return opening, closing


@dataclass
class MonthlyBreakdown:
    """Aggregated data for one billing month."""
    year: int
    month: int
    label: str
    income: float
    expenses: float
    net: float
    categories: list[CategoryBreakdown] = field(default_factory=list)
    income_transactions: list[Transaction] = field(default_factory=list)

# ── Main entry: build the full report data ───────────────────────────────────

def build_report(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
    year: int | None = None,
    month: int | None = None,
) -> ReportData:
    """Aggregate all data needed for the report. No side effects."""
    from core.period import period_label

    by_category = combined_spending(bank_transactions, card_transactions)

    categories = []
    for cat_name, txs in sorted(
        by_category.items(),
        key=lambda x: sum(t.debit for t in x[1]),
        reverse=True,
    ):
        total = sum(tx.debit for tx in txs)
        if total > 0:
            categories.append(CategoryBreakdown(
                name=cat_name,
                total=total,
                transactions=sorted(txs, key=lambda t: t.debit, reverse=True),
            ))

    total_income = sum(
        tx.credit for tx in bank_transactions
        if tx.credit == tx.credit and tx.credit > 0
    )
    
    total_expenses = sum(cat.total for cat in categories)
    opening, closing = _compute_balances(bank_transactions)
    balance_change = closing - opening
    net = total_income - total_expenses
    cashflow = closing - opening

    income_txs = sorted(
        [tx for tx in bank_transactions if tx.credit == tx.credit and tx.credit > 0],
        key=lambda t: t.credit,
        reverse=True,
    )

    # Monthly breakdown is only meaningful when not filtering to a single month
    monthly = _monthly_breakdown(bank_transactions, card_transactions) if not month else []

    return ReportData(
        period_label=period_label(year, month),
        year=year,
        month=month,
        opening_balance=opening,
        closing_balance=closing,
        balance_change=balance_change,  # или balance_change
        total_income=total_income,
        total_expenses=total_expenses,
        net=net,
        categories=categories,
        income_transactions=income_txs,
        monthly_breakdown=monthly,
    )


def _monthly_breakdown(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
    cutoff_day: int = 16,
) -> list[MonthlyBreakdown]:
    """Break down income and expenses by billing month, with full category detail."""
    # Group transactions by billing month
    by_month: dict[tuple[int, int], dict] = defaultdict(
        lambda: {"bank": [], "card": []}
    )

    for tx in bank_transactions:
        bm = billing_month(tx.date, cutoff_day)
        by_month[(bm.year, bm.month)]["bank"].append(tx)

    for tx in card_transactions:
        bm = billing_month(tx.date, cutoff_day)
        by_month[(bm.year, bm.month)]["card"].append(tx)

    months_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    result = []
    for (year, month) in sorted(by_month.keys(), reverse=True):
        bank_txs = by_month[(year, month)]["bank"]
        card_txs = by_month[(year, month)]["card"]

        # Categories for this month
        cat_dict = combined_spending(bank_txs, card_txs)
        categories = []
        for cat_name, txs in sorted(
            cat_dict.items(),
            key=lambda x: sum(t.debit for t in x[1]),
            reverse=True,
        ):
            total = sum(tx.debit for tx in txs)
            if total > 0:
                categories.append(CategoryBreakdown(
                    name=cat_name,
                    total=total,
                    transactions=sorted(txs, key=lambda t: t.debit, reverse=True),
                ))

        # Income for this month
        income_txs = sorted(
            [tx for tx in bank_txs if tx.credit == tx.credit and tx.credit > 0],
            key=lambda t: t.credit,
            reverse=True,
        )
        income = sum(tx.credit for tx in income_txs)
        expenses = sum(cat.total for cat in categories)

        result.append(MonthlyBreakdown(
            year=year,
            month=month,
            label=f"{months_names[month]} {year}",
            income=income,
            expenses=expenses,
            net=income - expenses,
            categories=categories,
            income_transactions=income_txs,
        ))

    return result