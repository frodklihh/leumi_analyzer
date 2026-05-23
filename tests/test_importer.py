"""
Tests for importer.py
"""

from datetime import datetime

import pytest

from scripts.importer import (
    _parse_amount,
    parse_leumi_xls,
    load_file,
    Transaction,
)


class TestParseAmount:

    def test_simple_number(self):
        assert _parse_amount("100.00") == 100.00

    def test_number_with_comma(self):
        assert _parse_amount("5,403.92") == 5403.92

    def test_empty_string(self):
        assert _parse_amount("") == 0.0


class TestParseLeumiXls:

    def test_returns_transactions(
        self,
        tmp_path,
        sample_xls_content,
    ):
        f = tmp_path / "test.xls"

        f.write_text(
            sample_xls_content,
            encoding="utf-8",
        )

        result = parse_leumi_xls(f)

        assert len(result) == 3

    def test_transaction_fields(
        self,
        tmp_path,
        sample_xls_content,
    ):
        f = tmp_path / "test.xls"

        f.write_text(
            sample_xls_content,
            encoding="utf-8",
        )

        result = parse_leumi_xls(f)

        tx = result[0]

        assert isinstance(tx, Transaction)

        assert tx.date == datetime(2026, 5, 15)
        assert tx.description == "לאומי ויזה(כא)"
        assert tx.reference == "5992"
        assert tx.debit == 766.00
        assert tx.credit == 0.00
        assert tx.balance == 44172.07
        assert tx.source == "bank"

    def test_load_file(
        self,
        tmp_path,
        sample_xls_content,
    ):
        f = tmp_path / "statement.xls"

        f.write_text(
            sample_xls_content,
            encoding="utf-8",
        )

        result = load_file(f)

        assert len(result) == 3

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_file("missing.xls")