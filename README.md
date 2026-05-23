# leumi-analyzer

A personal finance analyzer for **Bank Leumi** checking accounts and **Cal Card** credit cards. Parses exported `.xls`/`.xlsx` files, auto-categorizes transactions, and generates an HTML report with EN/RU support.

---

## Installation

```bash
git clone https://github.com/frodklihh/leumi-analyzer.git
cd leumi-analyzer
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

> Requires **Python 3.11+**

---

## Usage

### 1. Place exported files into `reports/`

```
leumi-analyzer/
└── reports/
    ├── bank_statement.xls
    ├── cards_elena.xlsx
    └── cards_leonid.xlsx
```

### 2. Run from the project root

```bash
# Full report
python -m scripts.main reports/bank_statement.xls reports/cards_elena.xlsx reports/cards_leonid.xlsx

# Filter by year/month
python -m scripts.main reports/bank_statement.xls reports/cards_elena.xlsx --year 2026 --month 3

# Custom output path
python -m scripts.main reports/bank_statement.xls reports/cards_elena.xlsx --output reports/my_report.html
```

> Always use the `-m` flag when running scripts.

### Output

- **Console** — summary printed to stdout
- **HTML report** — saved to `reports/report.html` (or `--output` path), with EN/RU toggle

---

## Data Sources

| Source | Instructions |
|--------|-------------|
| **Bank Leumi** | Open checking account (עובר ושב) → select date range → export as `.xls` |
| **Cal Card** | Go to transaction details (פירוט עסקאות וזיכויים) → select range → download `.xlsx` |

---

## Project Structure

```
leumi-analyzer/
├── leumi_analyzer/        # Isolated package for categorization rules
│   ├── __init__.py
│   └── categorizer.py     # Auto-categorization rules
├── core/                  # Core business logic
│   ├── __init__.py
│   ├── analytics.py       # Report calculations
│   └── period.py          # Billing month logic (16→15 cycle)
├── views/                 # Presentation layer
│   ├── __init__.py
│   ├── console.py         # Terminal output
│   └── html.py            # HTML engine via Jinja2
├── scripts/               # CLI entry points
│   ├── __init__.py
│   ├── main.py            # Workflow orchestrator
│   └── importer.py        # File parser (xls/xlsx)
├── templates/
│   └── report.html        # HTML template with JS translation
├── tests/                 # pytest suite
└── reports/               # Input files & generated reports (git-ignored)
```

---

## Core Logic

| Concept | Description |
|---------|-------------|
| **Billing Month** | Implements the 16→15 cycle (`core/period.py`). Purchases after the 15th count toward the next billing month. |
| **Settlement Detection** | Matches lump-sum card payments in the bank statement to exclude them and avoid double-counting. |
| **Pending vs. Settled** | Card charges are marked *pending* if their billing month is later than the last bank-settled month. |
| **Testing** | Run `pytest` to verify parsers, rules, and calculation edge cases. |