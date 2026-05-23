"""
Shared fixtures for all tests.
"""
import pytest
from datetime import datetime
from importer import Transaction


@pytest.fixture
def sample_transactions():
    """Bank-style transactions across multiple billing months.

    Note: billing_month uses cutoff_day=16, so:
    - dates 1-15 belong to current calendar month's billing
    - dates 16-31 belong to NEXT calendar month's billing
    """
    return [
        # May billing month
        Transaction(
            date=datetime(2026, 5, 10),
            description="קרן מכבי-י",
            reference="25300",
            debit=204.61,
            credit=0.00,
            balance=56188.98,
            source="bank",
        ),
        Transaction(
            date=datetime(2026, 5, 8),
            description='מט"ב מרכז-י',
            reference="10018",
            debit=0.00,
            credit=2334.66,
            balance=60023.64,
            source="bank",
        ),
        Transaction(
            date=datetime(2026, 5, 1),
            description="חנות לא ידועה",
            reference="99999",
            debit=50.00,
            credit=0.00,
            balance=55000.00,
            source="bank",
        ),
        # April billing month
        Transaction(
            date=datetime(2026, 4, 10),
            description="פרעון הלוואה",
            reference="3858001",
            debit=1047.30,
            credit=0.00,
            balance=66541.41,
            source="bank",
        ),
        # March billing month
        Transaction(
            date=datetime(2026, 3, 8),
            description="אסותא-מרכזים-י",
            reference="40000",
            debit=0.00,
            credit=9443.31,
            balance=64211.58,
            source="bank",
        ),
    ]


@pytest.fixture
def sample_card_transactions():
    """Credit card detailed transactions."""
    return [
        Transaction(
            date=datetime(2026, 5, 10),
            description="שופרסל דיל קרית מוצקין",
            reference="",
            debit=234.56,
            credit=0.00,
            balance=0.00,
            source="credit_card",
        ),
        Transaction(
            date=datetime(2026, 5, 8),
            description="רמי לוי קרית חיים",
            reference="",
            debit=189.20,
            credit=0.00,
            balance=0.00,
            source="credit_card",
        ),
        Transaction(
            date=datetime(2026, 4, 20),
            description="וולט",
            reference="",
            debit=85.00,
            credit=0.00,
            balance=0.00,
            source="credit_card",
        ),
    ]


@pytest.fixture
def cc_settlement_tx():
    """Bank transaction representing a CC settlement (lump sum)."""
    return Transaction(
        date=datetime(2026, 3, 15),
        description="חיוב כרטיסי אשראי",
        reference="999",
        debit=2500.00,
        credit=0.00,
        balance=50000.00,
        source="bank",
    )


@pytest.fixture
def cc_refund_in_bank():
    """Bank credit that's actually a credit card refund."""
    return Transaction(
        date=datetime(2026, 3, 11),
        description="כרטיסי אשראי-י",
        reference="888",
        debit=0.00,
        credit=500.00,
        balance=52000.00,
        source="bank",
    )


@pytest.fixture
def card_refund_tx():
    """Card transaction with credit > 0 (a refund from the merchant)."""
    return Transaction(
        date=datetime(2026, 3, 6),
        description="TUI CRUISES VG.4413813",
        reference="",
        debit=0.00,
        credit=500.00,
        balance=0.00,
        source="credit_card",
    )


@pytest.fixture
def bank_fee_tx():
    """Bank service fee transaction."""
    return Transaction(
        date=datetime(2026, 5, 1),
        description="מסלול בסיסי",
        reference="111",
        debit=14.90,
        credit=0.00,
        balance=55000.00,
        source="bank",
    )


@pytest.fixture
def sample_xls_content():
    """Minimal HTML that mimics a real Leumi .xls export."""
    return """
    <HTML><body>
    <table><tr><td>בנק לאומי</td></tr></table>
    <table><tr><td>היתרה</td></tr></table>
    <table>
        <tr><td>תנועות בחשבון</td></tr>
        <tr><td>תאריך</td><td>תאריך ערך</td><td>תיאור</td><td>אסמכתא</td><td>בחובה</td><td>בזכות</td><td>היתרה בש"ח</td><td>הערה</td></tr>
        <tr><td>15/05/2026</td><td>15/05/2026</td><td>לאומי ויזה(כא)</td><td>5992</td><td>766.00</td><td>0.00</td><td>44,172.07</td><td></td></tr>
        <tr><td>10/05/2026</td><td>10/05/2026</td><td>קרן מכבי-י</td><td>25300</td><td>204.61</td><td>0.00</td><td>56,188.98</td><td></td></tr>
        <tr><td>08/05/2026</td><td>08/05/2026</td><td>מט"ב מרכז-י</td><td>10018</td><td>0.00</td><td>2,334.66</td><td>60,023.64</td><td></td></tr>
    </table>
    </body></HTML>
    """