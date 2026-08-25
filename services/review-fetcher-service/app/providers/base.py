"""Abstraction over any external source of reviews for a place."""

from abc import ABC, abstractmethod

from ..models import Review


class ReviewsProvider(ABC):
    @abstractmethod
    async def fetch_reviews(self, place_id: str) -> list[Review]:
        """Return whatever reviews the upstream source currently exposes for this place."""
        raise NotImplementedError
