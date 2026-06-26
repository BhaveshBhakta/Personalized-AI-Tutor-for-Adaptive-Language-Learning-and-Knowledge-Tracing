from datetime import datetime

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    rating: str


class FlashcardResponse(BaseModel):

    flashcard_id: int

    word: str

    translation: str

    mastery: int

    stability: float

    difficulty: float

    retrievability: float

    interval_days: int

    next_review: datetime

    review_count: int

    lapses: int