"""Abstraction over persisting a place's reviews for a given month."""

from abc import ABC, abstractmethod

from ..models import Review


class ReviewsRepository(ABC):
    @abstractmethod
    def save_reviews(self, place_id: str, year: int, month: int, reviews: list[Review]) -> str:
        """Persist the reviews and return the storage key they were written under."""
        raise NotImplementedError
