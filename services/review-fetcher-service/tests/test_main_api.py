import os

os.environ.setdefault("GOOGLE_PLACES_API_KEY", "test-key")

from fastapi.testclient import TestClient

from app.main import app, get_review_fetch_service
from app.models import FetchReviewsResult
from app.providers.google_places import GooglePlacesAPIError


class StubService:
    def __init__(self, result=None, error: Exception | None = None):
        self._result = result
        self._error = error

    async def fetch_and_store(self, place_id: str, year: int, month: int) -> FetchReviewsResult:
        if self._error:
            raise self._error
        return self._result


def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fetch_reviews_returns_result_on_success():
    expected = FetchReviewsResult(
        place_id="place123", year=2024, month=3, redis_key="reviews:place123:2024-03", review_count=0, reviews=[]
    )
    app.dependency_overrides[get_review_fetch_service] = lambda: StubService(result=expected)

    client = TestClient(app)
    response = client.post("/reviews/fetch", json={"place_id": "place123", "year": 2024, "month": 3})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["redis_key"] == "reviews:place123:2024-03"


def test_fetch_reviews_returns_502_on_google_api_error():
    app.dependency_overrides[get_review_fetch_service] = lambda: StubService(
        error=GooglePlacesAPIError("NOT_FOUND", "no such place")
    )

    client = TestClient(app)
    response = client.post("/reviews/fetch", json={"place_id": "bad-id", "year": 2024, "month": 3})

    app.dependency_overrides.clear()
    assert response.status_code == 502


def test_fetch_reviews_rejects_invalid_month():
    with TestClient(app) as client:
        response = client.post("/reviews/fetch", json={"place_id": "place123", "year": 2024, "month": 13})
    assert response.status_code == 422
