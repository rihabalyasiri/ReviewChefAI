"""HTTP entry point for the review-fetcher-service."""

from contextlib import asynccontextmanager

import httpx
import redis
from fastapi import Depends, FastAPI, HTTPException

from .config import get_settings
from .models import FetchReviewsRequest, FetchReviewsResult
from .providers.google_places import GooglePlacesAPIError, GooglePlacesReviewsProvider
from .repositories.redis_repository import RedisReviewsRepository
from .services.review_fetch_service import ReviewFetchService

settings = get_settings()
resources: dict[str, object] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    resources["http_client"] = httpx.AsyncClient(timeout=10.0)
    resources["redis_client"] = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )
    yield
    await resources["http_client"].aclose()
    resources["redis_client"].close()


app = FastAPI(title="Review Fetcher Service", lifespan=lifespan)


def get_review_fetch_service() -> ReviewFetchService:
    provider = GooglePlacesReviewsProvider(settings.google_places_api_key, resources["http_client"])
    repository = RedisReviewsRepository(resources["redis_client"], settings.review_cache_ttl_seconds)
    return ReviewFetchService(provider, repository)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reviews/fetch", response_model=FetchReviewsResult)
async def fetch_reviews(
    request: FetchReviewsRequest,
    service: ReviewFetchService = Depends(get_review_fetch_service),
) -> FetchReviewsResult:
    try:
        return await service.fetch_and_store(request.place_id, request.year, request.month)
    except GooglePlacesAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
