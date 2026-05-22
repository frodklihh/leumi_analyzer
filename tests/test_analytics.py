"""
Tests for core/analytics.py
"""

import pytest
from datetime import datetime
from importer import Transaction
from categorizer import categorize
from core.analytics import (
    filter_transactions,
    combined_spending,
    build_report,
    UNKNOWN_CATEGORY,
    ReportData,
    CategoryBreakdown,
    MonthlyBreakdown,
)


class TestFilterTransactions:
    def test_filter_by_year(self, sample_transactions):
        result = filter_transactions(sample_transactions, year=2026)
        assert all(tx.date.year == 2026 for tx in result)
        assert len(result) == len(sample_transactions)

    def test_filter_by_year_no_match(self, sample_transactions):
        result = filter_transactions(sample_transactions, year=2020)
        assert result == []

    def test_filter_by_billing_month_excludes_after_cutoff(self, sample_transactions):
        # 15 May → billing June, so filter for billing May should exclude it
        result = filter_transactions(sample_transactions, year=2026, month=5)
        days = [tx.date.day for tx in result if tx.date.month == 5]
        assert all(d < 15 for d in days)

    def test_filter_includes_late_previous_month(self, sample_transactions):
        # 17 April → billing May
        result = filter_transactions(sample_transactions, year=2026, month=5)
        april_late = [tx for tx in result if tx.date.month == 4 and tx.date.day >= 15]
        assert len(april_late) > 0

    def test_empty_list(self):
        assert filter_transactions([], year=2026) == []


class TestCombinedSpending:
    def test_excludes_credit_card_payments(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        by_cat = combined_spending(sample_transactions, [])
        # לאומי ויזה(כא) is a credit card payment, must be excluded
        all_descriptions = [tx.description for txs in by_cat.values() for tx in txs]
        assert "לאומי ויזה(כא)" not in all_descriptions

    def test_includes_card_purchases(self, sample_card_transactions):
        sample_card_transactions = categorize(sample_card_transactions)
        by_cat = combined_spending([], sample_card_transactions)
        all_descriptions = [tx.description for txs in by_cat.values() for tx in txs]
        assert "שופרסל דיל קרית מוצקין" in all_descriptions

    def test_excludes_income(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        by_cat = combined_spending(sample_transactions, [])
        for txs in by_cat.values():
            for tx in txs:
                assert tx.debit > 0


class TestBuildReport:
    def test_returns_report_data(self, sample_transactions, sample_card_transactions):
        sample_transactions = categorize(sample_transactions)
        sample_card_transactions = categorize(sample_card_transactions)
        report = build_report(sample_transactions, sample_card_transactions, year=2026)
        assert isinstance(report, ReportData)

    def test_categories_sorted_descending(self, sample_transactions, sample_card_transactions):
        sample_transactions = categorize(sample_transactions)
        sample_card_transactions = categorize(sample_card_transactions)
        report = build_report(sample_transactions, sample_card_transactions)
        totals = [cat.total for cat in report.categories]
        assert totals == sorted(totals, reverse=True)

    def test_net_equals_income_minus_expenses(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        assert abs(report.net - (report.total_income - report.total_expenses)) < 0.01

    def test_period_label_set(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [], year=2026, month=5)
        assert report.period_label == "May 2026"

    def test_no_monthly_breakdown_when_single_month(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [], year=2026, month=5)
        assert report.monthly_breakdown == []

    def test_monthly_breakdown_when_year_only(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [], year=2026)
        assert len(report.monthly_breakdown) > 0

    def test_monthly_breakdown_items_are_monthly_breakdown(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [], year=2026)
        for m in report.monthly_breakdown:
            assert isinstance(m, MonthlyBreakdown)

    def test_income_transactions_have_positive_credit(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        for tx in report.income_transactions:
            assert tx.credit > 0

    def test_income_transactions_sorted_descending(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        credits = [tx.credit for tx in report.income_transactions]
        assert credits == sorted(credits, reverse=True)


class TestBalances:
    def test_opening_balance_computed(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        assert report.opening_balance > 0

    def test_empty_returns_zero_balance(self):
        report = build_report([], [])
        assert report.opening_balance == 0.0
        assert report.closing_balance == 0.0


class TestCategoryBreakdown:
    def test_total_matches_sum_of_transactions(self, sample_card_transactions):
        sample_card_transactions = categorize(sample_card_transactions)
        report = build_report([], sample_card_transactions)
        for cat in report.categories:
            assert abs(cat.total - sum(tx.debit for tx in cat.transactions)) < 0.01

    def test_transactions_sorted_by_debit_descending(self, sample_card_transactions):
        sample_card_transactions = categorize(sample_card_transactions)
        report = build_report([], sample_card_transactions)
        for cat in report.categories:
            debits = [tx.debit for tx in cat.transactions]
            assert debits == sorted(debits, reverse=True)