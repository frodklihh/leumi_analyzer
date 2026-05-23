"""
Tests for core/period.py
"""

from datetime import datetime
from core.period import billing_month, period_label


class TestBillingMonth:
    def test_before_cutoff_stays_in_month(self):
        assert billing_month(datetime(2026, 5, 10)) == datetime(2026, 5, 1)

    def test_day_before_cutoff_stays_in_month(self):
        assert billing_month(datetime(2026, 5, 15)) == datetime(2026, 5, 1)

    def test_on_cutoff_moves_to_next(self):
        assert billing_month(datetime(2026, 5, 16)) == datetime(2026, 6, 1)

    def test_after_cutoff_moves_to_next(self):
        assert billing_month(datetime(2026, 5, 20)) == datetime(2026, 6, 1)


class TestPeriodLabel:
    def test_year_and_month(self):
        assert period_label(2026, 5) == "May 2026"
        assert period_label(2026, 1) == "January 2026"
        assert period_label(2026, 12) == "December 2026"

    def test_year_only(self):
        assert period_label(2026, None) == "Year 2026"

    def test_month_only(self):
        assert period_label(None, 5) == "May (all years)"

    def test_no_filter(self):
        assert period_label(None, None) == "All time"