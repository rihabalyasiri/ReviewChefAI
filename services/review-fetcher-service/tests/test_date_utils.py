from datetime import datetime, timezone

from app.date_utils import filter_reviews_by_range, month_date_range
from app.models import Review


def make_review(time: int) -> Review:
    return Review(
        author_name="A. Reviewer",
        rating=5,
        text="Great food!",
        relative_time_description="a week ago",
        time=time,
    )


def test_month_date_range_handles_short_february():
    start, end = month_date_range(2023, 2)
    assert start == datetime(2023, 2, 1, tzinfo=timezone.utc)
    assert end == datetime(2023, 2, 28, 23, 59, 59, tzinfo=timezone.utc)


def test_month_date_range_handles_leap_february():
    start, end = month_date_range(2024, 2)
    assert end == datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc)


def test_filter_reviews_by_range_is_inclusive_of_boundaries():
    start, end = month_date_range(2024, 3)
    reviews = [
        make_review(int(start.timestamp())),  # exactly first instant
        make_review(int(end.timestamp())),  # exactly last instant
        make_review(int(start.timestamp()) - 1),  # just before the month
        make_review(int(end.timestamp()) + 1),  # just after the month
    ]

    result = filter_reviews_by_range(reviews, start, end)

    assert len(result) == 2
    assert result[0].time == int(start.timestamp())
    assert result[1].time == int(end.timestamp())
