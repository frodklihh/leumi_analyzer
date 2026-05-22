"""
views/console.py - terminal output of report data
"""

from core.analytics import ReportData, UNKNOWN_CATEGORY
from importer import Transaction


def print_summary(report: ReportData) -> None:
    """Print the overall summary block."""
    balance_sign = "+" if report.balance_change >= 0 else "-"
    net_sign = "+" if report.real_net >= 0 else "-"

    print("\n" + "═" * 52)
    print(f"  ACCOUNT SUMMARY - {report.period_label}")
    print("═" * 52)

    print("\n  📊 Account movement")
    print(f"  Opening balance:  ₪{report.opening_balance:>10,.2f}")
    print(f"  Closing balance:  ₪{report.closing_balance:>10,.2f}")
    print(f"  Δ Balance:        {balance_sign}₪{abs(report.balance_change):>9,.2f}")

    print("\n  💰 Real picture")
    print(f"  Total income:     ₪{report.total_income:>10,.2f}")
    print(f"  Real expenses:    ₪{report.total_expenses:>10,.2f}")
    print(f"  Real net:         {net_sign}₪{abs(report.real_net):>9,.2f}")

    if report.pending_cc > 0:
        print("\n  ⏳ Pending")
        print(f"  Will be charged:  ₪{report.pending_cc:>10,.2f}")


def print_categories(report: ReportData) -> None:
    """Print spending by category."""
    print("\n" + "═" * 52)
    print("  SPENDING BY CATEGORY")
    print("═" * 52)
    for cat in report.categories:
        print(f"  {cat.name:<32} ₪{cat.total:>10,.2f}")


def print_monthly_breakdown(report: ReportData) -> None:
    """Print monthly breakdown table (only for multi-month reports)."""
    if not report.monthly_breakdown:
        return

    print("\n" + "═" * 52)
    print("  MONTHLY BREAKDOWN")
    print("═" * 52)
    print(f"  {'Month':<20} {'Income':>12} {'Expenses':>12} {'Net':>12}")
    print(f"  {'-' * 20} {'-' * 12} {'-' * 12} {'-' * 12}")
    for m in report.monthly_breakdown:
        sign = "+" if m.net >= 0 else "-"
        print(
            f"  {m.label:<20} "
            f"₪{m.income:>10,.2f} "
            f"₪{m.expenses:>10,.2f} "
            f"{sign}₪{abs(m.net):>9,.2f}"
        )


def print_unknown_transactions(card_transactions: list[Transaction]) -> None:
    """Print transactions that could not be categorized."""
    unknown = [tx for tx in card_transactions if tx.category == UNKNOWN_CATEGORY]
    if not unknown:
        return

    print("\n" + "═" * 52)
    print("  UNKNOWN TRANSACTIONS")
    print("═" * 52)
    for tx in unknown[:50]:
        print(f"  {tx.date.strftime('%d.%m')}  {tx.description:<35} ₪{tx.debit:>8,.2f}")


def print_report(report: ReportData, card_transactions: list[Transaction]) -> None:
    """Print the full report to terminal."""
    print_summary(report)
    print_categories(report)
    print_monthly_breakdown(report)
    print_unknown_transactions(card_transactions)