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

    card = Flashcard(
        vocabulary_id=vocabulary_id,
        user_id=user_id,
    )

    db.add(card)
    db.commit()

    return {
        "message":
        "Flashcard created"
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
            Flashcard.vocabulary_id
            == Vocabulary.id,
        )
        .filter(
            Flashcard.user_id == user_id,
            Flashcard.next_review <= now,
        )
        .all()
    )

    return [
        {
            "flashcard_id": card.id,
            "word": vocab.word,
            "translation":
            vocab.translation,
            "mastery":
            card.mastery_score,
        }
        for card, vocab in cards
    ]

@router.post(
    "/review/{flashcard_id}"
)
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

    card.review_count += 1

    if data.rating == "again":
        card.mastery_score = max(
            0,
            card.mastery_score - 10,
        )

        card.next_review = (
            datetime.utcnow()
            + timedelta(minutes=10)
        )

    elif data.rating == "hard":
        card.mastery_score += 2

        card.next_review = (
            datetime.utcnow()
            + timedelta(days=1)
        )

    elif data.rating == "good":
        card.mastery_score += 5

        card.next_review = (
            datetime.utcnow()
            + timedelta(days=3)
        )

    elif data.rating == "easy":
        card.mastery_score += 10

        card.next_review = (
            datetime.utcnow()
            + timedelta(days=7)
        )

    db.commit()

    return {
        "message":
        "Review saved"
    }