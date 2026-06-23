from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.vocabulary import Vocabulary
from app.models.flashcard import Flashcard
from app.models.learning_profile import LearningProfile

from app.core.auth import get_current_user_id

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/")
def dashboard(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    total_words = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id == user_id
        )
        .count()
    )

    due_reviews = (
        db.query(Flashcard)
        .filter(
            Flashcard.user_id == user_id,
            Flashcard.next_review <= datetime.utcnow(),
        )
        .count()
    )

    profile = (
        db.query(LearningProfile)
        .filter(
            LearningProfile.user_id == user_id
        )
        .first()
    )

    if not profile:

        profile = LearningProfile(
            user_id=user_id,
            target_level="A1",
            daily_goal_minutes=30,
            xp=0,
            streak=0,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "total_words": total_words,
        "due_reviews": due_reviews,
        "daily_goal_minutes":
            profile.daily_goal_minutes,
        "xp":
            profile.xp,
        "streak":
            profile.streak,
    }


@router.get("/study-plan")
def study_plan(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    due_reviews = (
        db.query(Flashcard)
        .filter(
            Flashcard.user_id == user_id,
            Flashcard.next_review <= datetime.utcnow(),
        )
        .count()
    )

    return {
        "reviews": due_reviews,
        "new_words": 5,
        "grammar_exercises": 10,
        "conversation_minutes": 5,
    }