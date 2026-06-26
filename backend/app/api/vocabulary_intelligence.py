from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.vocabulary import (
    Vocabulary
)

from app.core.auth import (
    get_current_user_id
)

router = APIRouter(
    prefix="/vocabulary-intelligence",
    tags=["Vocabulary Intelligence"],
)


@router.get("/weak-words")
def weak_words(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    words = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id
            == user_id
        )
        .order_by(
            Vocabulary.mastery_score.asc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "id": word.id,
            "word": word.word,
            "translation":
            word.translation,
            "mastery":
            word.mastery_score,
        }
        for word in words
    ]