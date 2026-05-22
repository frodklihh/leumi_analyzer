"""
core/period.py - billing month logic
"""

from datetime import datetime


def billing_month(date: datetime, cutoff_day: int = 16) -> datetime:
    """Map a date to its billing month (16th-to-15th cycle).

    Dates on/after cutoff_day belong to the NEXT calendar month.
    Returns a datetime pinned to the 1st of the billing month.
    """
    if date.day >= cutoff_day:
        if date.month == 12:
            return datetime(date.year + 1, 1, 1)
        return datetime(date.year, date.month + 1, 1)
    return datetime(date.year, date.month, 1)


def period_label(year: int | None, month: int | None) -> str:
    """Build a human-readable period label."""
    months = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if year and month:
        return f"{months[month]} {year}"
    if year:
        return f"Year {year}"
    if month:
        return f"{months[month]} (all years)"
    return "All time"