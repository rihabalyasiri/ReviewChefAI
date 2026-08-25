"""Redis-backed storage for a place's monthly reviews."""

import json

import redis

from ..models import Review
from .base import ReviewsRepository


class RedisReviewsRepository(ReviewsRepository):
    def __init__(self, client: redis.Redis, ttl_seconds: int | None = None):
        self._client = client
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def build_key(place_id: str, year: int, month: int) -> str:
        return f"reviews:{place_id}:{year:04d}-{month:02d}"

    def save_reviews(self, place_id: str, year: int, month: int, reviews: list[Review]) -> str:
        key = self.build_key(place_id, year, month)
        payload = json.dumps([review.model_dump() for review in reviews])
        self._client.set(key, payload, ex=self._ttl_seconds)
        return key
