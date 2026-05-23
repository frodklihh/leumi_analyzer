# Leumi Analyzer

Python CLI tool that analyzes Bank Leumi statements together with Cal credit card exports and produces a clear HTML report with the real financial picture.

Built to bridge the gap between what the bank shows you (only settled transactions) and what you actually spent (including pending card charges).

## What it does

- Parses Bank Leumi (`.xls`) statements and Cal credit card (`.xlsx`) exports
- Categorizes transactions automatically based on description patterns
- Detects credit card settlements and excludes them from double-counting
- Tracks pending card charges that haven't hit the bank yet
- Tracks past-period charges that got settled during the current period
- Excludes refunds and bank-fee artifacts from income calculations
- Handles the 16→15 billing month cycle correctly
- Generates an interactive HTML report with collapsible sections and tabbed views

## Report sections

### 📊 Account movement
What actually moved through the bank account during the period.

- **Opening Balance** — balance at the start of the period
- **Closing Balance** — balance at the end of the period
- **Δ Balance** — net movement; only reflects what the bank has already settled

### 💰 Real picture
The full financial picture, including transactions still pending on cards.

- **Total Income** — all credits to the bank account (salary, refunds, transfers)
- **Real Expenses** — bank expenses (excluding card settlements) + all card transactions from Cal exports
- **Real Net** — `Total Income − Real Expenses`; the honest period result

### ⏳ Pending charges
Card purchases not yet reflected in the bank balance.

- **Will be charged soon** — sum of card transactions whose billing month hasn't been settled yet

### 📜 Past period charges *(when applicable)*
Card purchases from before the period that the bank settled during it.

- **Settled in this period** — explains discrepancies between Δ Balance and Real Net

### The reconciliation

```
Δ Balance ≈ Real Net − Pending + Past Charges
```

## Installation

```bash
git clone https://github.com/<user>/leumi-analyzer.git
cd leumi-analyzer
python -m venv .venv
source .venv/bin/activate     # Linux/Mac
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Requires Python 3.11+.

## Usage

Place exported files into `reports/`:

```
leumi-analyzer/
└── reports/
    ├── bank_statement.xls
    ├── cards_elena.xlsx
    └── cards_leonid.xlsx
```

### Run

```bash
# Full report, all time
python main.py reports/bank_statement.xls reports/cards_elena.xlsx reports/cards_leonid.xlsx

# Filter by year (uses billing month logic, 16→15)
python main.py reports/bank_statement.xls reports/cards_elena.xlsx reports/cards_leonid.xlsx --year 2026

# Filter by specific month
python main.py reports/bank_statement.xls reports/cards_elena.xlsx reports/cards_leonid.xlsx --year 2026 --month 3

# Custom output location
python main.py reports/bank_statement.xls reports/cards_elena.xlsx --year 2026 --output reports/my_report.html
```

Multiple card files are supported — pass them all as positional arguments.

### Output

- Console summary printed to stdout
- HTML report saved to `reports/report.html` (or the `--output` path)

## Where to get the data

### Bank Leumi

1. Log in to https://www.leumi.co.il
2. Open **עובר ושב** (checking account)
3. Select the desired date range
4. Click **ייצוא** (export) and save the `.xls` file

### Cal credit card

1. Log in to https://www.cal-online.co.il
2. Go to **פירוט עסקאות וזיכויים** (transaction & refund details)
3. Select the date range
4. Download the `.xlsx` file

For multi-cardholder households, download a separate file per card and pass all of them as arguments.

## Project structure

```
leumi-analyzer/
├── main.py                    # CLI entry point
├── importer.py                # File parsing (xls/xlsx → Transaction list)
├── categorizer.py             # Auto-categorization rules
├── core/
│   ├── analytics.py           # Report building, all calculations
│   └── period.py              # Billing month logic (16→15 cycle)
├── views/
│   ├── console.py             # Terminal output
│   └── html.py                # HTML rendering via Jinja2
├── templates/
│   └── report.html            # HTML report template
├── tests/                     # pytest suite
└── reports/                   # Input files and generated reports
```

## Key concepts

### Billing month (16→15 cycle)

Israeli credit card billing runs from the 16th of one month to the 15th of the next (depends). A purchase made on December 16th belongs to the January billing cycle, not December.

The `core/period.py` module implements `billing_month(date)`, and all filtering and grouping use it instead of the calendar month.

### Credit card settlement detection

The bank statement shows credit card payments as single lump sums (e.g., "Visa charge: ₪4,500"), while the Cal export details every individual purchase. The analyzer:

- Detects settlement lines in the bank statement via Hebrew/English keyword matching
- Excludes them from expense totals to avoid double-counting
- Uses the difference between settlements and card spending to compute pending

### Pending vs. settled

A card transaction is considered **pending** if its billing month is later than the most recent billing month that the bank has settled. This computation always runs against the full dataset, not the filtered period, so "pending" always reflects the current real-world state.

### Refund handling

Card refunds (Cal entries with `credit > 0`) and their corresponding bank credits (lines containing CC-related keywords with positive credit) are handled to avoid double-counting between the two data sources.

## Testing

```bash
pytest
```

Tests cover parser correctness, categorization rules, billing month logic, and report-building edge cases.

