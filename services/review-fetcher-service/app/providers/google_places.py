"""Google Places API (legacy Place Details endpoint) review provider.

Known limitation: the Places API only ever returns up to 5 reviews for a place
(the "most relevant" or, with ``reviews_sort=newest``, the most recent ones) and
offers no server-side date filtering or pagination. Requesting a month in the
past will often yield zero matches once results are filtered down to that
month. Full historical access requires the Google Business Profile API instead
(OAuth as the verified business owner) - see the service README.
"""

import httpx

from ..models import Review
from .base import ReviewsProvider


class GooglePlacesAPIError(RuntimeError):
    def __init__(self, status: str, message: str | None):
        self.status = status
        self.message = message
        super().__init__(f"Google Places API returned status={status}: {message or 'no error message'}")


class GooglePlacesReviewsProvider(ReviewsProvider):
    BASE_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    def __init__(self, api_key: str, http_client: httpx.AsyncClient):
        self._api_key = api_key
        self._http_client = http_client

    async def fetch_reviews(self, place_id: str) -> list[Review]:
        response = await self._http_client.get(
            self.BASE_URL,
            params={
                "place_id": place_id,
                "fields": "reviews",
                "reviews_sort": "newest",
                "key": self._api_key,
            },
        )
        response.raise_for_status()
        payload = response.json()

        status = payload.get("status", "UNKNOWN_ERROR")
        if status != "OK":
            raise GooglePlacesAPIError(status, payload.get("error_message"))

        raw_reviews = payload.get("result", {}).get("reviews", [])
        return [
            Review(
                author_name=raw["author_name"],
                rating=raw["rating"],
                text=raw.get("text", ""),
                relative_time_description=raw.get("relative_time_description", ""),
                time=raw["time"],
                language=raw.get("language"),
            )
            for raw in raw_reviews
        ]
