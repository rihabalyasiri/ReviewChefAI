"""Helpers for computing and applying a calendar-month date range."""

import calendar
from datetime import datetime, timezone

from .models import Review


def month_date_range(year: int, month: int) -> tuple[datetime, datetime]:
    """Return the (first instant, last instant) of the given calendar month, in UTC."""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return start, end


def filter_reviews_by_range(reviews: list[Review], start: datetime, end: datetime) -> list[Review]:
    """Keep only reviews whose timestamp falls within [start, end], inclusive."""
    start_ts, end_ts = start.timestamp(), end.timestamp()
    return [review for review in reviews if start_ts <= review.time <= end_ts]
