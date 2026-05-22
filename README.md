# leumi-analyzer

Analyze Bank Leumi account statements and credit card transactions. Breaks down spending by category, supports billing-month logic (15th-to-15th cycle), and produces an interactive HTML report with month-by-month drilldown.

## Features

- Parses Leumi `.xls` (HTML) and `.xlsx` bank statements
- Parses Leumi credit card detailed transactions
- Supports multiple credit cards in a single report
- Keyword-based categorization (Hebrew + English)
- Billing-month logic (15th-to-15th, configurable)
- Interactive HTML report with expandable categories and monthly breakdown
- Filter by year and/or month
- Terminal output for quick checks 

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full report for 2026, single card
python main.py reports/bank_statement.xls reports/card.xlsx --year 2026

# Multiple cards (e.g. family accounts)
python main.py reports/bank_statement.xls reports/card_a.xlsx reports/card_b.xlsx --year 2026

# Filter to a single billing month
python main.py reports/bank_statement.xls reports/card.xlsx --year 2026 --month 4

# Custom output path
python main.py reports/bank_statement.xls reports/card.xlsx --year 2026 --output reports/2026.html
```

Open the generated HTML in a browser:

```bash
start reports/report.html        # Windows
open reports/report.html          # macOS
xdg-open reports/report.html      # Linux
```

## How to export your data from Leumi

### Bank statement

1. Log in to leumi.co.il
2. Go to **תנועות בחשבון** (Account movements)
3. Select your date range
4. Click **ייצוא לאקסל** (Export to Excel) — save as `.xls`

### Credit card detailed transactions (from Cal)

Leumi-branded credit cards are issued through **Cal** (cal-online.co.il). Detailed transactions are exported from there, not from the Leumi site.

1. Log in to cal-online.co.il
2. Go to **פירוט עסקאות וזיכויים** (Transactions and credits)
3. Select your date range
4. Export to Excel (`.xlsx`)
5. Repeat for each card you want included

## Project structure

```
leumi-analyzer/
├── main.py                 # CLI entry point
├── importer.py             # Leumi .xls / .xlsx parsers
├── categorizer.py          # Keyword-based categorization
├── core/
│   ├── analytics.py        # Pure data calculations
│   └── period.py           # Billing-month logic
├── views/
│   ├── console.py          # Terminal output
│   └── html.py             # HTML rendering via Jinja2
├── templates/
│   └── report.html         # Jinja2 HTML template
├── tests/                  # pytest suite
├── reports/                # Input files & generated reports
└── requirements.txt
```

## Configuration

### Adding or editing categories

Open `categorizer.py` and edit the `CATEGORIES` dictionary:

```python
CATEGORIES = {
    "🏠 House & Billing": ["שכירות", "ארנונה", "חשמל", ...],
    "🍎 Groceries": ["שופרסל", "רמי לוי", ...],
    "🐾 Pets": ["וטרינר", "petshop"],
}
```

Transactions that don't match any keyword land in **❓ Other**. Check that
section in the report — if you see recurring descriptions there, add their
keywords to the right category.

### Special rules

- A check (`שיק`) or digital transfer (`העברה דיגיטל`) of approximately
  ₪4,500 is automatically classified as rent (House & Billing).
- Other checks and transfers go to the `💸 Transactions` category.
- Credit card payment lines in the bank statement (`לאומי ויזה`,
  `כרטיסי אשראי`) are excluded from spending totals to avoid double counting
  with the detailed card transactions.

### Billing month

The billing month runs from the 15th of one month to the 14th of the next.
Transactions on or after the 15th of May are billed in June. This matches
how Leumi credit card cycles work. Change the `cutoff_day` parameter in
`core/period.py` if you need a different cycle.

## Running tests

```bash
pytest tests -v
```

## Tech stack

- Python 3.11+
- pandas + openpyxl for `.xlsx` parsing
- beautifulsoup4 for Leumi's HTML-disguised `.xls`
- Jinja2 for HTML templating
- pytest for tests