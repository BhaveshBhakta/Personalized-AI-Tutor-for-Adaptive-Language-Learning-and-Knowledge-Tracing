from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.core.auth import get_current_user_id

from app.models.flashcard import Flashcard
from app.models.grammar_progress import GrammarProgress
from app.models.vocabulary import Vocabulary

router = APIRouter(
    prefix="/planner",
    tags=["Planner"]
)

@router.get("/today")
def get_today_plan(
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

    vocab_count = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id == user_id
        )
        .count()
    )

    grammar = (
        db.query(GrammarProgress)
        .filter(
            GrammarProgress.user_id == user_id
        )
        .all()
    )

    weak_topic = None

    if grammar:

        weakest = min(
            grammar,
            key=lambda x:
            x.mastery_score
        )

        weak_topic = {
            "topic_id":
            weakest.topic_id,

            "mastery":
            weakest.mastery_score,
        }

    return {
        "due_reviews":
        due_reviews,

        "vocabulary_count":
        vocab_count,

        "weak_topic":
        weak_topic,

        "recommended_flashcards":
        min(
            max(due_reviews, 5),
            20
        ),

        "recommended_new_words":
        5,

        "recommended_grammar":
        10,
    }