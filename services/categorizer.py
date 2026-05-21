# categorizer.py

"""
categorizer.py - transaction categorization
"""

import re
from typing import Optional
from importer import Transaction


UNKNOWN_CATEGORY = "❓ Other"


MERCHANT_ALIASES = {
    "am pm": "am:pm",
    "ampm": "am:pm",
    "am pm dizengoff": "am:pm",
    "super pharm": "סופר פארם",
    "superpharm": "סופר פארם",
    "mcdonalds": "מקדונלד",
}


CATEGORIES: dict[str, list[str]] = {
    "🍎 Groceries": [
        "שופרסל",
        "רמי לוי",
        "מגה",
        "ויקטורי",
        "יינות ביתן",
        "אושר עד",
        "מחסני השוק",
        "קרפור",
        "am:pm",
        "טיב טעם",
        "קשת טעמים",
        "שוק פייסל",
        "החמניה",
        "שלי",
        "שוק",
        "ירקות",
        "פירות",
    ],

    "🍽️ Restaurants & Cafes": [
        "וולט",
        "wolt",
        "10bis",
        "מסעדה",
        "קפה",
        "פיצה",
        "סושי",
        "המבורגר",
        "פלאפל",
        "מקדונלד",
        "ארומה",
        "דיווין",
        "איזי פאף",
    ],

    "🚗 Transport": [
        "דלק",
        "פז",
        "סונול",
        "דור אלון",
        "אגד",
        "דן",
        "רכבת",
        "רב קו",
        "גט",
        "יאנגו",
        "חניה",
        "פז אפליקציית יילו",
        "פריים מוטורס",
    ],

    "🏥 Health & Medical": [
        "מכבי",
        "כללית",
        "לאומית",
        "מאוחדת",
        "סופר פארם",
        "רוסמן",
        "גוד פארם",
        "בית מרקחת",
    ],

    "📱 Phone & Internet": [
        "סלקום",
        "פרטנר",
        "פלאפון",
        "HOT",
        "012",
        "019",
    ],

    "🛍️ Shopping & Clothing": [
        "zara",
        "h&m",
        "קסטרו",
        "פוקס",
        "amazon",
        "apple",
        "istore",
        "ksp",
        "ivory",
        "ikea",
        "we shose",
    ],

    "🏋️ Sport & Fitness": [
        "gym",
        "מכון כושר",
        "הולמס פלייס",
    ],

    "🎬 Entertainment": [
        "netflix",
        "spotify",
        "apple tv",
        "disney",
        "קולנוע",
    ],

    "✈️ Travel": [
        "booking",
        "airbnb",
        "ryanair",
        "wizz",
        "easyjet",
        "מלון",
    ],

  "💰 Income": [
    "משכורת",
    "שכר",
    "זיכוי",
    "החזר",
    "ביטוח לאומי",
    "מט\"ב",
    "מטב",
    ],
}


def normalize_description(text: str) -> str:
    text = text.lower()

    locations = [
        "tel aviv",
        "tlv",
        "jerusalem",
        "haifa",
        "beer sheva",
        "תל אביב",
        "חיפה",
        "ירושלים",
    ]

    for loc in locations:
        text = text.replace(loc, "")

    text = re.sub(r"\d+", "", text)

    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace(":", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def canonicalize(text: str) -> str:
    text = normalize_description(text)

    for alias, canonical in MERCHANT_ALIASES.items():
        if alias in text:
            return canonical

    return text


def _match_keywords(description: str) -> Optional[str]:
    desc = canonicalize(description)

    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in desc:
                return category

    return None


def categorize(transactions: list[Transaction]) -> list[Transaction]:
    for tx in transactions:
        category = _match_keywords(tx.description)
        tx.category = category if category else UNKNOWN_CATEGORY

    return transactions