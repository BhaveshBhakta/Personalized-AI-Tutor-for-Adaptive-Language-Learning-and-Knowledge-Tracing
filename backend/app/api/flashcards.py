from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.flashcard import Flashcard
from app.models.learning_profile import LearningProfile
from app.models.vocabulary import Vocabulary

from app.schemas.flashcard import (
    ReviewRequest,
)

from app.core.auth import (
    get_current_user_id,
)

from app.services.learning_engine import (
    LearningEngine,
)

router = APIRouter(
    prefix="/flashcards",
    tags=["Flashcards"],
)


@router.post("/{vocabulary_id}")
def create_flashcard(
    vocabulary_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
            detail="Vocabulary not found",
        )

    existing = (
        db.query(Flashcard)
        .filter(
            Flashcard.user_id == user_id,
            Flashcard.vocabulary_id == vocabulary_id,
        )
        .first()
    )

    if existing:
        return {
            "message": "Flashcard already exists",
            "flashcard_id": existing.id,
        }

    card = Flashcard(
        vocabulary_id=vocabulary_id,
        user_id=user_id,
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "message": "Flashcard created",
        "flashcard_id": card.id,
    }


@router.get("/due")
def due_cards(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    cards = (
        db.query(Flashcard)
        .join(
            Vocabulary,
            Flashcard.vocabulary_id == Vocabulary.id,
        )
        .filter(
            Flashcard.user_id == user_id,
            Flashcard.next_review <= datetime.utcnow(),
        )
        .all()
    )

    results = []

    for card in cards:

        vocab = (
            db.query(Vocabulary)
            .filter(
                Vocabulary.id == card.vocabulary_id
            )
            .first()
        )

        results.append({

            "flashcard_id": card.id,

            "word": vocab.word,

            "translation": vocab.translation,

            "mastery": card.mastery_score,

            "stability": card.stability,

            "difficulty": card.difficulty,

            "retrievability": card.retrievability,

            "interval_days": card.interval_days,

            "next_review": card.next_review,

            "review_count": card.review_count,

            "lapses": card.lapses,

        })

    return results


@router.post("/review/{flashcard_id}")
def review(
    flashcard_id: int,
    data: ReviewRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
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
            detail="Flashcard not found",
        )

    profile = (
        db.query(LearningProfile)
        .filter(
            LearningProfile.user_id == user_id
        )
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Learning profile not found",
        )

    LearningEngine.review_flashcard(
        card=card,
        profile=profile,
        rating=data.rating,
    )

    db.commit()
    db.refresh(card)
    db.refresh(profile)

    return {

        "message": "Review saved",

        "xp": profile.xp,

        "mastery": card.mastery_score,

        "stability": round(
            card.stability,
            2,
        ),

        "difficulty": round(
            card.difficulty,
            2,
        ),

        "retrievability": round(
            card.retrievability,
            2,
        ),

        "interval_days": card.interval_days,

        "next_review": card.next_review,

        "review_count": card.review_count,

        "lapses": card.lapses,

    }