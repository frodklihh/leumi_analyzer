from datetime import datetime


def billing_month(date: datetime, cutoff_day: int = 16) -> datetime:
    if date.day >= cutoff_day:
        if date.month == 12:
            return datetime(date.year + 1, 1, 1)
        return datetime(date.year, date.month + 1, 1)
    return datetime(date.year, date.month, 1)


def period_label(year: int | None, month: int | None) -> str:
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