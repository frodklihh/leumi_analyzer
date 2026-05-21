"""
reporter.py - summary, unknown transactions, and HTML export
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from importer import Transaction

UNKNOWN_CATEGORY = "❓ Other"


def _billing_month(date: datetime, cutoff_day: int = 15) -> datetime:
    """Map a date to its billing month (15th-to-15th cycle)."""
    if date.day >= cutoff_day:
        if date.month == 12:
            return datetime(date.year + 1, 1, 1)
        return datetime(date.year, date.month + 1, 1)
    return datetime(date.year, date.month, 1)


def _period_label(year: int | None, month: int | None) -> str:
    """Build a human-readable period label."""
    months = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if year and month:
        return f"{months[month]} {year}"
    if year:
        return f"Year {year}"
    if month:
        return f"{months[month]} (all years)"
    return "All time"


def filter_transactions(
    transactions: list[Transaction],
    year: int | None = None,
    month: int | None = None,
    cutoff_day: int = 15,
) -> list[Transaction]:
    """Filter by billing year/month (15th-to-15th cycle)."""
    result = transactions
    if year:
        result = [tx for tx in result if _billing_month(tx.date, cutoff_day).year == year]
    if month:
        result = [tx for tx in result if _billing_month(tx.date, cutoff_day).month == month]
    return result


def _is_card_payment(tx: Transaction) -> bool:
    """Detect bank transactions that are just credit card payments."""
    desc = tx.description.lower()
    markers = ["ויזה", "כרטיסי אשראי", "ישראכרט", "max", "cal", "מקס", "כאל"]
    return any(m in desc for m in markers)


def _combined_spending(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
) -> dict[str, list[Transaction]]:
    """Merge bank + card transactions by category, excluding card payments from bank."""
    by_category: dict[str, list[Transaction]] = defaultdict(list)

    for tx in bank_transactions:
        if tx.debit > 0 and not _is_card_payment(tx):
            by_category[tx.category].append(tx)

    for tx in card_transactions:
        if tx.debit > 0:
            by_category[tx.category].append(tx)

    return by_category


def combined_summary(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
) -> None:
    """Print account summary and combined spending by category."""
    total_income = sum(
        tx.credit for tx in bank_transactions
        if tx.credit == tx.credit and tx.credit > 0
    )

    by_category = _combined_spending(bank_transactions, card_transactions)
    total_expenses = sum(tx.debit for txs in by_category.values() for tx in txs)
    net = total_income - total_expenses
    sign = "+" if net >= 0 else "-"

    print("\n" + "═" * 52)
    print("  OVERALL ACCOUNT SUMMARY")
    print("═" * 52)
    print(f"\n  Total income:    ₪{total_income:>10,.2f}")
    print(f"  Total expenses:  ₪{total_expenses:>10,.2f}")
    print(f"  Net balance:     {sign}₪{abs(net):>9,.2f}")

    print("\n" + "═" * 52)
    print("  SPENDING BY CATEGORY")
    print("═" * 52)
    for category, txs in sorted(
        by_category.items(),
        key=lambda x: sum(t.debit for t in x[1]),
        reverse=True,
    ):
        amount = sum(tx.debit for tx in txs)
        if amount > 0:
            print(f"  {category:<32} ₪{amount:>10,.2f}")


def print_unknown_transactions(transactions: list[Transaction]) -> None:
    """Print transactions that could not be categorized."""
    unknown = [tx for tx in transactions if tx.category == UNKNOWN_CATEGORY]
    if not unknown:
        return

    print("\n" + "═" * 52)
    print("  UNKNOWN TRANSACTIONS")
    print("═" * 52)
    for tx in unknown[:50]:
        print(f"  {tx.date.strftime('%d.%m')}  {tx.description:<35} ₪{tx.debit:>8,.2f}")


def save_html_report(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
    output_path: str = "reports/report.html",
    year: int | None = None,
    month: int | None = None,
) -> None:
    """Save a styled HTML report with Income/Expenses tabs."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    period_label = _period_label(year, month)

    total_income = sum(
        tx.credit for tx in bank_transactions
        if tx.credit == tx.credit and tx.credit > 0
    )

    by_category = _combined_spending(bank_transactions, card_transactions)
    total_expenses = sum(tx.debit for txs in by_category.values() for tx in txs)
    net = total_income - total_expenses

# ── Balance: opening (before period) and closing (after period) ───────────
    if bank_transactions:
        min_date = min(tx.date for tx in bank_transactions)
        max_date = max(tx.date for tx in bank_transactions)

        # On the earliest date, the FIRST transaction by row order has the HIGHEST
        # balance (each subsequent transaction reduces it). So opening = max balance
        # on that day + the debit (or - credit) of that very first transaction.
        first_day_txs = [tx for tx in bank_transactions if tx.date == min_date]
        first_tx = max(first_day_txs, key=lambda t: t.balance)
        opening_balance = first_tx.balance - first_tx.credit + first_tx.debit

        # Closing = lowest balance on the last day (the last transaction of the day)
        last_day_txs = [tx for tx in bank_transactions if tx.date == max_date]
        closing_balance = min(last_day_txs, key=lambda t: t.balance).balance
    else:
        opening_balance = 0.0
        closing_balance = 0.0
    # ── Expenses tab content ─────────────────────────────────────────────────
    expenses_html = ""
    for category, txs in sorted(
        by_category.items(),
        key=lambda x: sum(t.debit for t in x[1]),
        reverse=True,
    ):
        total = sum(tx.debit for tx in txs)
        if total <= 0:
            continue

        rows = "".join(f"""
            <tr>
                <td>{tx.date.strftime('%d.%m.%Y')}</td>
                <td>{tx.description}</td>
                <td class="amount expense-amount">₪{tx.debit:,.2f}</td>
            </tr>""" for tx in sorted(txs, key=lambda t: t.debit, reverse=True))

        is_unknown = category == UNKNOWN_CATEGORY
        expenses_html += f"""
        <details class="category-card{' unknown-section' if is_unknown else ''}">
            <summary class="category-header">
                <span>{category}</span>
                <span class="amount expense-amount">₪{total:,.2f}</span>
            </summary>
            <div class="table-container">
                <table>
                    <thead><tr><th>Date</th><th>Description</th><th>Amount</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </details>"""

    # ── Income tab content ───────────────────────────────────────────────────
    income_txs = [
        tx for tx in bank_transactions
        if tx.credit == tx.credit and tx.credit > 0
    ]
    income_rows = "".join(f"""
        <tr>
            <td>{tx.date.strftime('%d.%m.%Y')}</td>
            <td>{tx.description}</td>
            <td class="amount income-amount">₪{tx.credit:,.2f}</td>
        </tr>""" for tx in sorted(income_txs, key=lambda t: t.credit, reverse=True))

    income_html = f"""
    <div class="income-table">
        <table>
            <thead><tr><th>Date</th><th>Description</th><th>Amount</th></tr></thead>
            <tbody>{income_rows}</tbody>
        </table>
    </div>""" if income_rows else "<p style='color:#888; padding:16px'>No income transactions found.</p>"

    net_class = "income-amount" if net >= 0 else "expense-amount"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leumi Analyzer Report - {period_label}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f4f6f8; padding: 24px; color: #222; }}
        h1 {{ margin-bottom: 8px; font-size: 1.8rem; }}
        .subtitle {{ color: #666; margin-bottom: 32px; font-size: 0.9rem; }}
        .period-badge {{
            display: inline-block;
            background: #4361ee;
            color: white;
            padding: 4px 12px;
            border-radius: 999px;
            font-weight: 600;
            margin-right: 8px;
        }}

        .summary {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }}
        .card {{ background: white; padding: 20px 24px; border-radius: 12px; min-width: 180px; flex: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .card h3 {{ margin-bottom: 8px; color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .value {{ font-size: 1.5rem; font-weight: 700; }}
        .income-amount {{ color: #2a9d8f; }}
        .expense-amount {{ color: #e63946; }}

        .tabs {{ display: flex; gap: 8px; margin-bottom: 20px; }}
        .tab-btn {{
            padding: 10px 24px; border: none; border-radius: 8px;
            font-size: 0.95rem; font-weight: 600; cursor: pointer;
            background: white; color: #666;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.15s;
        }}
        .tab-btn.active {{ background: #4361ee; color: white; }}

        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        .category-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .category-card[open] {{ box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
        .category-header {{ display: flex; justify-content: space-between; align-items: center; font-size: 1.05rem; font-weight: 600; cursor: pointer; list-style: none; }}
        .category-header::-webkit-details-marker {{ display: none; }}
        .category-header::after {{ content: "▼"; font-size: 12px; color: #aaa; transition: transform 0.2s; }}
        .category-card[open] .category-header::after {{ transform: rotate(180deg); }}

        .table-container {{ margin-top: 16px; padding-top: 16px; border-top: 1px solid #eee; }}
        .income-table {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}

        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        th {{ text-align: left; padding: 8px 10px; background: #f8f9fa; color: #666; font-size: 0.8rem; text-transform: uppercase; }}
        td {{ padding: 8px 10px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover td {{ background: #fafafa; }}
        .amount {{ text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }}
        .unknown-section {{ border: 1px dashed #e63946; }}
    </style>
</head>
<body>
    <h1>🏦 Leumi Analyzer Report</h1>
    <p class="subtitle">
        <span class="period-badge">📅 {period_label}</span>
        Generated on {datetime.now().strftime('%d.%m.%Y %H:%M')}
    </p>

    <div class="summary">
        <div class="card">
            <h3>Opening Balance</h3>
            <div class="value">₪{opening_balance:,.2f}</div>
        </div>
        <div class="card">
            <h3>Total Income</h3>
            <div class="value income-amount">₪{total_income:,.2f}</div>
        </div>
        <div class="card">
            <h3>Total Expenses</h3>
            <div class="value expense-amount">₪{total_expenses:,.2f}</div>
        </div>
        <div class="card">
            <h3>Net Change</h3>
            <div class="value {net_class}">₪{net:,.2f}</div>
        </div>
        <div class="card">
            <h3>Closing Balance</h3>
            <div class="value">₪{closing_balance:,.2f}</div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab(event, 'expenses')">💸 Expenses</button>
        <button class="tab-btn" onclick="switchTab(event, 'income')">💰 Income</button>
    </div>

    <div id="expenses" class="tab-content active">
        {expenses_html}
    </div>

    <div id="income" class="tab-content">
        {income_html}
    </div>

    <script>
        function switchTab(e, name) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            e.target.classList.add('active');
        }}
    </script>
</body>
</html>"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n💾 Report saved to: {out_file.resolve()}")