from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.flashcard import Flashcard
from app.models.vocabulary import Vocabulary

from app.schemas.flashcard import (
    ReviewRequest,
)

from app.core.auth import (
    get_current_user_id,
)

router = APIRouter(
    prefix="/flashcards",
    tags=["Flashcards"],
)


@router.post("/{vocabulary_id}")
def create_flashcard(
    vocabulary_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    vocab = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.id == vocabulary_id,
            Vocabulary.user_id == user_id,
        )
        .first()
    )

    if not vocab:
        raise HTTPException(
            status_code=404,
            detail="Word not found",
        )

    existing = (
        db.query(Flashcard)
        .filter(
            Flashcard.vocabulary_id == vocabulary_id,
            Flashcard.user_id == user_id,
        )
        .first()
    )

    if existing:
        return {
            "message": "Flashcard already exists"
        }

    card = Flashcard(
        vocabulary_id=vocabulary_id,
        user_id=user_id,
        review_count=0,
        mastery_score=0,
        stability=1.0,
        difficulty=5.0,
        retrievability=1.0,
        interval_days=0,
        lapses=0,
        last_review=datetime.utcnow(),
        next_review=datetime.utcnow(),
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "message": "Flashcard created",
        "flashcard_id": card.id,
    }


@router.get("/due")
def get_due_cards(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    now = datetime.utcnow()

    cards = (
        db.query(
            Flashcard,
            Vocabulary,
        )
        .join(
            Vocabulary,
            Flashcard.vocabulary_id == Vocabulary.id,
        )
        .filter(
            Flashcard.user_id == user_id,
            Flashcard.next_review <= now,
        )
        .order_by(
            Flashcard.next_review.asc()
        )
        .all()
    )

    return [
        {
            "flashcard_id": card.id,
            "word": vocab.word,
            "translation": vocab.translation,
            "mastery": card.mastery_score,
            "stability": round(card.stability, 2),
            "difficulty": round(card.difficulty, 2),
            "retrievability": round(card.retrievability, 2),
            "interval_days": card.interval_days,
            "next_review": card.next_review,
            "review_count": card.review_count,
            "lapses": card.lapses,
        }
        for card, vocab in cards
    ]


@router.post("/review/{flashcard_id}")
def review_flashcard(
    flashcard_id: int,
    data: ReviewRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    card = (
        db.query(Flashcard)
        .filter(
            Flashcard.id == flashcard_id,
            Flashcard.user_id == user_id,
        )
        .first()
    )

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Card not found",
        )

    now = datetime.utcnow()

    card.review_count += 1
    card.last_review = now

    if data.rating == "again":

        card.lapses += 1

        card.mastery_score = max(
            0,
            card.mastery_score - 10,
        )

        card.difficulty = min(
            10.0,
            card.difficulty + 0.5,
        )

        card.stability = max(
            1.0,
            card.stability * 0.7,
        )

        card.interval_days = 0

    elif data.rating == "hard":

        card.mastery_score = min(
            100,
            card.mastery_score + 2,
        )

        card.difficulty = max(
            1.0,
            card.difficulty - 0.1,
        )

        card.stability *= 1.2

        card.interval_days = max(
            1,
            int(card.stability),
        )

    elif data.rating == "good":

        card.mastery_score = min(
            100,
            card.mastery_score + 5,
        )

        card.difficulty = max(
            1.0,
            card.difficulty - 0.2,
        )

        card.stability *= 1.6

        card.interval_days = max(
            2,
            int(card.stability),
        )

    elif data.rating == "easy":

        card.mastery_score = min(
            100,
            card.mastery_score + 10,
        )

        card.difficulty = max(
            1.0,
            card.difficulty - 0.4,
        )

        card.stability *= 2.0

        card.interval_days = max(
            4,
            int(card.stability),
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid rating",
        )

    card.retrievability = min(
        1.0,
        card.mastery_score / 100,
    )

    card.next_review = (
        now +
        timedelta(
            days=card.interval_days
        )
    )

    db.commit()
    db.refresh(card)

    return {
        "message": "Review saved",
        "mastery": card.mastery_score,
        "stability": round(card.stability, 2),
        "difficulty": round(card.difficulty, 2),
        "retrievability": round(card.retrievability, 2),
        "interval_days": card.interval_days,
        "next_review": card.next_review,
        "review_count": card.review_count,
        "lapses": card.lapses,
    }