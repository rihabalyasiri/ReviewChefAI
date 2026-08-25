import httpx
import pytest
import respx

from app.providers.google_places import GooglePlacesAPIError, GooglePlacesReviewsProvider

PLACE_ID = "place123"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_reviews_parses_successful_response():
    respx.get(GooglePlacesReviewsProvider.BASE_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "OK",
                "result": {
                    "reviews": [
                        {
                            "author_name": "Jane Doe",
                            "rating": 4,
                            "text": "Loved the pasta.",
                            "relative_time_description": "2 days ago",
                            "time": 1700000000,
                            "language": "en",
                        }
                    ]
                },
            },
        )
    )

    async with httpx.AsyncClient() as client:
        provider = GooglePlacesReviewsProvider(api_key="key", http_client=client)
        reviews = await provider.fetch_reviews(PLACE_ID)

    assert len(reviews) == 1
    assert reviews[0].author_name == "Jane Doe"
    assert reviews[0].time == 1700000000


@pytest.mark.asyncio
@respx.mock
async def test_fetch_reviews_raises_on_non_ok_status():
    respx.get(GooglePlacesReviewsProvider.BASE_URL).mock(
        return_value=httpx.Response(
            200,
            json={"status": "NOT_FOUND", "error_message": "no such place"},
        )
    )

    async with httpx.AsyncClient() as client:
        provider = GooglePlacesReviewsProvider(api_key="key", http_client=client)
        with pytest.raises(GooglePlacesAPIError):
            await provider.fetch_reviews(PLACE_ID)
