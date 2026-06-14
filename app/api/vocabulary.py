from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.vocabulary import Vocabulary

from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyResponse,
)

from app.core.auth import get_current_user_id

router = APIRouter(
    prefix="/vocabulary",
    tags=["Vocabulary"],
)

@router.post("/", status_code=201)

@router.post("/")
def create_word(
    data: VocabularyCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    word = Vocabulary(
        user_id=user_id,
        word=data.word,
        article=data.article,
        plural=data.plural,
        translation=data.translation,
        example_sentence=data.example_sentence,
    )

    db.add(word)
    db.commit()
    db.refresh(word)

    return {
        "message": "Word added",
        "id": word.id,
    }

@router.get(
    "/",
    response_model=list[VocabularyResponse]
)
def get_words(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id == user_id
        )
        .all()
    )

@router.get(
    "/{word_id}",
    response_model=VocabularyResponse
)
def get_word(
    word_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    word = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.id == word_id,
            Vocabulary.user_id == user_id,
        )
        .first()
    )

    if not word:
        raise HTTPException(
            status_code=404,
            detail="Word not found",
        )

    return word

@router.delete("/{word_id}")
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    word = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.id == word_id,
            Vocabulary.user_id == user_id,
        )
        .first()
    )

    if not word:
        raise HTTPException(
            status_code=404,
            detail="Word not found",
        )

    db.delete(word)
    db.commit()

    return {
        "message": "Deleted"
    }

@router.get("/search/{query}")
def search_words(
    query: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):
    return (
        db.query(Vocabulary)
        .filter(
            Vocabulary.user_id == user_id,
            Vocabulary.word.ilike(
                f"%{query}%"
            )
        )
        .all()
    )