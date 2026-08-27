"""Orchestrates fetching reviews for a place and storing the ones within a month."""

from ..date_utils import filter_reviews_by_range, month_date_range
from ..models import FetchReviewsResult
from ..providers.base import ReviewsProvider
from ..repositories.base import ReviewsRepository


class ReviewFetchService:
    def __init__(self, provider: ReviewsProvider, repository: ReviewsRepository):
        self._provider = provider
        self._repository = repository

    async def fetch_and_store(self, place_id: str, year: int, month: int) -> FetchReviewsResult:
        all_reviews = await self._provider.fetch_reviews(place_id)

        start, end = month_date_range(year, month)
        reviews_in_month = filter_reviews_by_range(all_reviews, start, end)

        redis_key = self._repository.save_reviews(place_id, year, month, reviews_in_month)

        return FetchReviewsResult(
            place_id=place_id,
            year=year,
            month=month,
            redis_key=redis_key,
            review_count=len(reviews_in_month),
            reviews=reviews_in_month,
        )
