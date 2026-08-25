import pytest

from app.date_utils import month_date_range
from app.models import Review
from app.providers.base import ReviewsProvider
from app.repositories.base import ReviewsRepository
from app.services.review_fetch_service import ReviewFetchService


def make_review(time: int) -> Review:
    return Review(
        author_name="A. Reviewer",
        rating=5,
        text="Great food!",
        relative_time_description="a week ago",
        time=time,
    )


class FakeProvider(ReviewsProvider):
    def __init__(self, reviews: list[Review]):
        self._reviews = reviews

    async def fetch_reviews(self, place_id: str) -> list[Review]:
        return self._reviews


class FakeRepository(ReviewsRepository):
    def __init__(self):
        self.saved: dict | None = None

    def save_reviews(self, place_id: str, year: int, month: int, reviews: list[Review]) -> str:
        key = f"reviews:{place_id}:{year:04d}-{month:02d}"
        self.saved = {"key": key, "reviews": reviews}
        return key


@pytest.mark.asyncio
async def test_fetch_and_store_only_persists_reviews_within_the_month():
    start, end = month_date_range(2024, 3)
    in_month = make_review(int(start.timestamp()))
    out_of_month = make_review(int(start.timestamp()) - 100)

    provider = FakeProvider([in_month, out_of_month])
    repository = FakeRepository()
    service = ReviewFetchService(provider, repository)

    result = await service.fetch_and_store("place123", 2024, 3)

    assert result.review_count == 1
    assert result.reviews == [in_month]
    assert repository.saved["reviews"] == [in_month]
    assert result.redis_key == "reviews:place123:2024-03"
