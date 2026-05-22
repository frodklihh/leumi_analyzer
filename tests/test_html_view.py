"""
Tests for views/html.py
"""

import pytest
from categorizer import categorize
from core.analytics import build_report
from views.html import render_html, save_html_report


class TestRenderHtml:
    def test_returns_string(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        html = render_html(report)
        assert isinstance(html, str)
        assert len(html) > 0

    def test_contains_period_label(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [], year=2026, month=5)
        html = render_html(report)
        assert "May 2026" in html

    def test_contains_amounts(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        html = render_html(report)
        # Some category total must appear
        assert "₪" in html

    def test_monthly_tab_only_when_data(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        # With month filter — no monthly tab
        report = build_report(sample_transactions, [], year=2026, month=5)
        html = render_html(report)
        assert "Monthly" not in html or "📊 Monthly" not in html

        # Without month filter — monthly tab present
        report = build_report(sample_transactions, [], year=2026)
        html = render_html(report)
        assert "📊 Monthly" in html

    def test_valid_html_structure(self, sample_transactions):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        html = render_html(report)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html


class TestSaveHtmlReport:
    def test_creates_file(self, sample_transactions, tmp_path):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        output = tmp_path / "report.html"
        save_html_report(report, str(output))
        assert output.exists()

    def test_file_not_empty(self, sample_transactions, tmp_path):
        sample_transactions = categorize(sample_transactions)
        report = build_report(sample_transactions, [])
        output = tmp_path / "report.html"
        save_html_report(report, str(output))
        assert output.stat().st_size > 1000  # at least some real content