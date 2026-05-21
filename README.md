Markdown

# leumi_analyzer

Analyze Bank Leumi account statements and credit card transactions to get interactive HTML dashboards and console breakdowns.

## Installation

```bash
pip install -r requirements.txt

Usage
Bash

python main.py bank_statement.xls card_transactions.xlsx

python main.py bank_statement.xls card_transactions.xlsx --year 2026 --month 5

How to export your files from Leumi
Bank Statement (.xls)

    Log in to leumi.co.il

    Go to תנועות בחשבון

    Select your date range

    Click ייצוא לאקסל

    Save the .xls file

Credit Card Transactions (.xlsx)

    Log in to leumi.co.il

    Go to חיובי כרטיסי אשראи

    Select your card and relevant billing cycle

    Click ייצוא לאקסל

    Save the .xlsx file

Project structure

leumi_analyzer/
├── importer.py
├── categorizer.py
├── reporter.py
├── main.py
├── requirements.txt
└── README.md
Adding or editing categories

Open categorizer.py and edit the CATEGORIES dictionary:
Python

CATEGORIES = {
    "🏠 Housing": ["שכירות", "ארנונה"],
    "🍎 Groceries": ["שופרסל", "רמי לוי"],
    "🐶 Pet": ["veterinary", "וטרינר", "petshop"],
}

Features & Reports
Interactive HTML Report

The script automatically builds a clean dashboard located in your local directory (reports/report.html). It includes:

    Overall Metrics: Top cards displaying Total Income, Total Expenses, and Net Balance.

    Smart Category Accordions: Spending groups are sorted by high-to-low totals. Each row can be clicked to toggle open a detailed inner table showing individual transactions, dates, and amounts without cluttering your view.

    Isolated Unknowns Section: An independent section at the bottom to check and resolve uncategorized entries.