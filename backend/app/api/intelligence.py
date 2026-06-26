from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.core.auth import get_current_user_id

from app.models.grammar_progress import (
    GrammarProgress,
)

from app.models.grammar_topic import (
    GrammarTopic,
)

router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)


@router.get("/weak-topic")
def get_weak_topic(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    progress = (
        db.query(GrammarProgress)
        .filter(
            GrammarProgress.user_id == user_id
        )
        .all()
    )

    if not progress:

        return {
            "message":
            "No grammar progress yet"
        }

    weakest = min(
        progress,
        key=lambda x:
        x.mastery_score
    )

    topic = (
        db.query(GrammarTopic)
        .filter(
            GrammarTopic.id
            == weakest.topic_id
        )
        .first()
    )

    return {
        "topic":
        topic.title,

        "mastery":
        weakest.mastery_score,

        "recommendation":
        f"Practice {topic.title} today"
    }