"""
Shared fixtures for all tests.
"""

import pytest
from datetime import datetime

from importer import Transaction


@pytest.fixture
def sample_transactions():
    return [
        Transaction(
            date=datetime(2026, 5, 15),
            description="לאומי ויזה(כא)",
            reference="5992",
            debit=766.00,
            credit=0.00,
            balance=44172.07,
            source="bank",
        ),
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
            date=datetime(2026, 4, 17),
            description="WOLT TEL AVIV",
            reference="77579",
            debit=110.00,
            credit=0.00,
            balance=56010.19,
            source="credit_card",
        ),
        Transaction(
            date=datetime(2026, 4, 10),
            description="AM:PM DIZENGOFF",
            reference="3858001",
            debit=147.30,
            credit=0.00,
            balance=66541.41,
            source="credit_card",
        ),
        Transaction(
            date=datetime(2026, 5, 1),
            description="חנות לא ידועה",
            reference="99999",
            debit=50.00,
            credit=0.00,
            balance=55000.00,
            source="credit_card",
        ),
    ]


@pytest.fixture
def sample_xls_content():
    return """
    <HTML>
    <body>
    <table>
        <tr><td>בנק לאומי</td></tr>
    </table>

    <table>
        <tr><td>היתרה</td></tr>
    </table>

    <table>
        <tr><td>תנועות בחשבון</td></tr>

        <tr>
            <td>תאריך</td>
            <td>תאריך ערך</td>
            <td>תיאור</td>
            <td>אסמכתא</td>
            <td>בחובה</td>
            <td>בזכות</td>
            <td>היתרה</td>
        </tr>

        <tr>
            <td>15/05/2026</td>
            <td>15/05/2026</td>
            <td>לאומי ויזה(כא)</td>
            <td>5992</td>
            <td>766.00</td>
            <td>0.00</td>
            <td>44,172.07</td>
        </tr>

        <tr>
            <td>10/05/2026</td>
            <td>10/05/2026</td>
            <td>קרן מכבי-י</td>
            <td>25300</td>
            <td>204.61</td>
            <td>0.00</td>
            <td>56,188.98</td>
        </tr>

        <tr>
            <td>08/05/2026</td>
            <td>08/05/2026</td>
            <td>מט"ב מרכז-י</td>
            <td>10018</td>
            <td>0.00</td>
            <td>2,334.66</td>
            <td>60,023.64</td>
        </tr>

    </table>
    </body>
    </HTML>
    """