from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.grammar_topic import (
    GrammarTopic,
)

from app.models.grammar_question import (
    GrammarQuestion
)

router = APIRouter(
    prefix="/grammar",
    tags=["Grammar"],
)

@router.get("/")
def get_topics(
    db: Session = Depends(get_db),
):
    return (
        db.query(GrammarTopic)
        .all()
    )

@router.get(
    "/topic/{topic_id}/questions"
)
def get_questions(
    topic_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(
            GrammarQuestion
        )
        .filter(
            GrammarQuestion.topic_id
            == topic_id
        )
        .all()
    )

@router.post(
    "/question/{question_id}/answer"
)
def answer_question(
    question_id: int,
    answer: str,
    db: Session = Depends(get_db),
):
    question = (
        db.query(
            GrammarQuestion
        )
        .filter(
            GrammarQuestion.id
            == question_id
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    is_correct = (
        answer.strip().lower()
        ==
        question.correct_answer.strip().lower()
    )

    return {
        "correct": is_correct,
        "expected": question.correct_answer,
    }