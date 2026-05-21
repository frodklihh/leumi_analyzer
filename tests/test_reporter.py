"""
Tests for reporter.py
"""

from categorizer import categorize

from reporter import (
    filter_transactions,
    combined_summary,
    print_unknown_transactions,
)


class TestFilterTransactions:

    def test_filter_by_year(
        self,
        sample_transactions,
    ):
        result = filter_transactions(
            sample_transactions,
            year=2026,
        )

        assert len(result) == len(sample_transactions)

    def test_filter_by_month(
        self,
        sample_transactions,
    ):
        result = filter_transactions(
            sample_transactions,
            month=5,
        )

        assert len(result) == 4


class TestCombinedSummary:

    def test_prints_summary(
        self,
        sample_transactions,
        capsys,
    ):
        categorized = categorize(sample_transactions)

        bank = [
            tx for tx in categorized
            if tx.source == "bank"
        ]

        card = [
            tx for tx in categorized
            if tx.source == "credit_card"
        ]

        combined_summary(bank, card)

        output = capsys.readouterr().out

        assert "OVERALL ACCOUNT SUMMARY" in output

        assert "SPENDING BY CATEGORY" in output

    def test_prints_categories(
        self,
        sample_transactions,
        capsys,
    ):
        categorized = categorize(sample_transactions)

        bank = [
            tx for tx in categorized
            if tx.source == "bank"
        ]

        card = [
            tx for tx in categorized
            if tx.source == "credit_card"
        ]

        combined_summary(bank, card)

        output = capsys.readouterr().out

        assert "🍽️ Restaurants & Cafes" in output
        assert "🍎 Groceries" in output


class TestUnknownTransactions:

    def test_print_unknowns(
        self,
        sample_transactions,
        capsys,
    ):
        categorized = categorize(sample_transactions)

        print_unknown_transactions(categorized)

        output = capsys.readouterr().out

        assert "UNKNOWN TRANSACTIONS" in output
        assert "חנות לא ידועה" in output