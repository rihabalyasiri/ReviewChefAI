import json

import fakeredis

from app.models import Review
from app.repositories.redis_repository import RedisReviewsRepository


def make_review() -> Review:
    return Review(
        author_name="A. Reviewer",
        rating=5,
        text="Great food!",
        relative_time_description="a week ago",
        time=1700000000,
    )


def test_save_reviews_writes_expected_key_and_payload():
    client = fakeredis.FakeRedis(decode_responses=True)
    repository = RedisReviewsRepository(client)

    key = repository.save_reviews("place123", 2024, 3, [make_review()])

    assert key == "reviews:place123:2024-03"
    stored = json.loads(client.get(key))
    assert len(stored) == 1
    assert stored[0]["author_name"] == "A. Reviewer"


def test_save_reviews_applies_ttl_when_configured():
    client = fakeredis.FakeRedis(decode_responses=True)
    repository = RedisReviewsRepository(client, ttl_seconds=3600)

    key = repository.save_reviews("place123", 2024, 3, [make_review()])

    assert client.ttl(key) > 0


def test_build_key_pads_single_digit_months():
    assert RedisReviewsRepository.build_key("place123", 2024, 3) == "reviews:place123:2024-03"
