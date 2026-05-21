# reporter.py

"""
reporter.py - reporting utilities
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from importer import Transaction


def filter_transactions(
    transactions: list[Transaction],
    year: int | None = None,
    month: int | None = None,
) -> list[Transaction]:

    result = transactions

    if year:
        result = [
            tx for tx in result
            if tx.date.year == year
        ]

    if month:
        result = [
            tx for tx in result
            if tx.date.month == month
        ]

    return result


def combined_summary(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
) -> None:

    total_income = sum(
        tx.credit
        for tx in bank_transactions
    )

    total_expenses = sum(
        tx.debit
        for tx in bank_transactions
        if tx.debit > 0
    )

    net = total_income - total_expenses

    print("\n" + "═" * 52)
    print("  OVERALL ACCOUNT SUMMARY")
    print("═" * 52)

    print(f"\n  Total income:     ₪{total_income:>10,.2f}")
    print(f"  Total expenses:  ₪{total_expenses:>10,.2f}")

    sign = "+" if net >= 0 else "-"

    print(
        f"  Net balance:     "
        f"{sign}₪{abs(net):>9,.2f}"
    )

    print("\n" + "═" * 52)
    print("  SPENDING BY CATEGORY")
    print("═" * 52)

    by_category: dict[str, float] = defaultdict(float)

    for tx in card_transactions:
        by_category[tx.category] += tx.debit

    for category, amount in sorted(
        by_category.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        if amount > 0:
            print(
                f"  {category:<30} "
                f"₪{amount:>10,.2f}"
            )


def print_unknown_transactions(
    transactions: list[Transaction],
) -> None:

    unknown = [
        tx for tx in transactions
        if tx.category == "❓ Other"
    ]

    if not unknown:
        return

    print("\n" + "═" * 52)
    print("  UNKNOWN TRANSACTIONS")
    print("═" * 52)

    for tx in unknown[:50]:
        print(
            f"  {tx.date.strftime('%d.%m')} "
            f"{tx.description}"
        )


def save_html_report(
    bank_transactions: list[Transaction],
    card_transactions: list[Transaction],
    output_path: str = r"D:\MyProjects\leumi-analyzer\reports\report.html",
) -> None:

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    total_income = sum(
        tx.credit
        for tx in bank_transactions
    )

    total_expenses = sum(
        tx.debit
        for tx in bank_transactions
        if tx.debit > 0
    )

    net = total_income - total_expenses

    by_category: dict[str, list[Transaction]] = defaultdict(list)

    for tx in card_transactions:
        by_category[tx.category].append(tx)

    category_rows = ""

    for category, txs in sorted(
        by_category.items(),
        key=lambda x: sum(t.debit for t in x[1]),
        reverse=True,
    ):

        total = sum(tx.debit for tx in txs)

        if total <= 0:
            continue

        transactions_html = ""

        for tx in sorted(
            txs,
            key=lambda t: t.debit,
            reverse=True,
        ):

            if tx.debit <= 0:
                continue

            transactions_html += f"""
            <tr>
                <td>{tx.date.strftime('%d.%m.%Y')}</td>
                <td>{tx.description}</td>
                <td>₪{tx.debit:,.2f}</td>
            </tr>
            """

        category_rows += f"""
        <details class="category-card">
            <summary class="category-header">
                <span>{category}</span>
                <span>₪{total:,.2f}</span>
            </summary>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th>Amount</th>
                        </tr>
                    </thead>

                    <tbody>
                        {transactions_html}
                    </tbody>
                </table>
            </div>
        </details>
        """

    unknown_html = ""

    unknown_transactions = [
        tx for tx in card_transactions
        if tx.category == "❓ Other"
    ]

    if unknown_transactions:

        rows = ""

        for tx in unknown_transactions:

            rows += f"""
            <tr>
                <td>{tx.date.strftime('%d.%m.%Y')}</td>
                <td>{tx.description}</td>
                <td>₪{tx.debit:,.2f}</td>
            </tr>
            """

        unknown_html = f"""
        <details class="category-card unknown-section">
            <summary class="category-header">
                <span>❓ Unknown Transactions</span>
                <span>₪{sum(tx.debit for tx in unknown_transactions):,.2f}</span>
            </summary>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th>Amount</th>
                        </tr>
                    </thead>

                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </details>
        """

    html = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Leumi Analyzer Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 24px;
    color: #222;
}}

h1 {{
    margin-bottom: 8px;
}}

.subtitle {{
    color: #666;
    margin-bottom: 32px;
}}

.summary {{
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 32px;
}}

.card {{
    background: white;
    padding: 20px;
    border-radius: 12px;
    min-width: 220px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

.card h3 {{
    margin-top: 0;
    color: #666;
}}

.value {{
    font-size: 28px;
    font-weight: bold;
}}

.income {{
    color: #2a9d8f;
}}

.expense {{
    color: #e63946;
}}

.category-card {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: box-shadow 0.2s ease;
}}

.category-card[open] {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}}

.category-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    user-select: none;
    list-style: none;
}}

.category-header::after {{
    content: "▼";
    font-size: 14px;
    color: #888;
    margin-left: 12px;
    transition: transform 0.2s ease;
}}

.category-card[open] .category-header::after {{
    transform: rotate(180deg);
}}

.category-header::-webkit-details-marker {{
    display: none;
}}

.table-container {{
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #eee;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    text-align: left;
    padding: 10px;
    background: #f0f0f0;
}}

td {{
    padding: 10px;
    border-bottom: 1px solid #eee;
}}

tr:hover {{
    background: #fafafa;
}}

.unknown-section {{
    margin-top: 32px;
    border: 1px dashed #e63946;
}}

</style>

</head>

<body>

<h1>🏦 Leumi Analyzer Report</h1>

<p class="subtitle">
Generated on
{datetime.now().strftime('%d.%m.%Y %H:%M')}
</p>

<div class="summary">

    <div class="card">
        <h3>Total Income</h3>
        <div class="value income">
            ₪{total_income:,.2f}
        </div>
    </div>

    <div class="card">
        <h3>Total Expenses</h3>
        <div class="value expense">
            ₪{total_expenses:,.2f}
        </div>
    </div>

    <div class="card">
        <h3>Net Balance</h3>
        <div class="value">
            ₪{net:,.2f}
        </div>
    </div>

</div>

{category_rows}

{unknown_html}

</body>
</html>
"""

    with open(
        out_file,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(html)

    print(f"\n💾 HTML report saved to: {out_file.resolve()}")