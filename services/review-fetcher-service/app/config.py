"""Environment-driven settings for the review-fetcher-service."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    google_places_api_key: str
    redis_host: str
    redis_port: int
    redis_db: int
    review_cache_ttl_seconds: int | None


def get_settings() -> Settings:
    ttl_raw = os.environ.get("REVIEW_CACHE_TTL_SECONDS")
    return Settings(
        google_places_api_key=os.environ["GOOGLE_PLACES_API_KEY"],
        redis_host=os.environ.get("REDIS_HOST", "localhost"),
        redis_port=int(os.environ.get("REDIS_PORT", "6379")),
        redis_db=int(os.environ.get("REDIS_DB", "0")),
        review_cache_ttl_seconds=int(ttl_raw) if ttl_raw else None,
    )
