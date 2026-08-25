"""Pydantic schemas for the review-fetcher-service."""

from pydantic import BaseModel, Field, field_validator


class Review(BaseModel):
    author_name: str
    rating: int
    text: str
    relative_time_description: str
    time: int  # unix timestamp (seconds), as returned by the Google Places API
    language: str | None = None


class FetchReviewsRequest(BaseModel):
    place_id: str
    year: int
    month: int

    @field_validator("month")
    @classmethod
    def month_in_range(cls, value: int) -> int:
        if not 1 <= value <= 12:
            raise ValueError("month must be between 1 and 12")
        return value


class FetchReviewsResult(BaseModel):
    place_id: str
    year: int
    month: int
    redis_key: str
    review_count: int
    reviews: list[Review] = Field(default_factory=list)
