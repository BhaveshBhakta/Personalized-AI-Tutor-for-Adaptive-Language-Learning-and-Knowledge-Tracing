from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.german_word import GermanWord
from app.models.vocabulary import Vocabulary

from app.schemas.german_word import (
    GermanWordResponse,
)

from app.core.auth import (
    get_current_user_id,
)

router = APIRouter(
    prefix="/german-words",
    tags=["German Words"],
)


@router.get(
    "/",
    response_model=list[GermanWordResponse]
)
def get_words(
    db: Session = Depends(get_db),
):
    return (
        db.query(GermanWord)
        .order_by(
            GermanWord.frequency_rank
        )
        .limit(100)
        .all()
    )


@router.get(
    "/search/{query}",
    response_model=list[GermanWordResponse]
)
def search_words(
    query: str,
    db: Session = Depends(get_db),
):
    return (
        db.query(GermanWord)
        .filter(
            GermanWord.word.ilike(
                f"%{query}%"
            )
        )
        .limit(50)
        .all()
    )


@router.post("/{word_id}/add")
def add_to_vocabulary(
    word_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):
    german_word = (
        db.query(GermanWord)
        .filter(
            GermanWord.id == word_id
        )
        .first()
    )

    if not german_word:
        raise HTTPException(
            status_code=404,
            detail="Word not found",
        )

    existing = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id == user_id,
            Vocabulary.word == german_word.word,
        )
        .first()
    )

    if existing:
        return {
            "message": "Already added"
        }

    vocab = Vocabulary(
        user_id=user_id,
        word=german_word.word,
        article=german_word.article,
        plural=german_word.plural,
        translation=german_word.translation,
        difficulty=german_word.difficulty,
    )

    db.add(vocab)
    db.commit()
    db.refresh(vocab)

    return {
        "message": "Added to vocabulary",
        "vocabulary_id": vocab.id,
    }