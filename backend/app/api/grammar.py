from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.db.dependencies import get_db
from app.models.grammar_topic import (GrammarTopic,)
from app.models.grammar_question import (GrammarQuestion)
from app.models.grammar_progress import (GrammarProgress)
from app.core.auth import (get_current_user_id)
from app.models.learning_profile import (LearningProfile)

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
    user_id: int = Depends(
        get_current_user_id
    ),
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

    correct = (
        answer ==
        question.correct_answer
    )

    progress = (
        db.query(
            GrammarProgress
        )
        .filter(
            GrammarProgress.user_id
            == user_id,

            GrammarProgress.topic_id
            == question.topic_id,
        )
        .first()
    )

    if not progress:

        progress = GrammarProgress(
            user_id=user_id,
            topic_id=question.topic_id,
            correct_answers=0,
            total_answers=0,
            mastery_score=0,
        )

        db.add(progress)

    else:

        if progress.correct_answers is None:
            progress.correct_answers = 0

        if progress.total_answers is None:
            progress.total_answers = 0

        if progress.mastery_score is None:
            progress.mastery_score = 0

    progress.total_answers += 1

    if correct:
        progress.correct_answers += 1

    progress.mastery_score = int(
        (
            progress.correct_answers
            /
            progress.total_answers
        ) * 100
    )

    profile = (
        db.query(
            LearningProfile
        )
        .filter(
            LearningProfile.user_id
            == user_id
        )
        .first()
    )

    if profile:

        if correct:
            profile.xp += 10
        else:
            profile.xp += 2

    db.commit()

    return {
        "correct": correct,
        "expected":
        question.correct_answer,

        "mastery":
        progress.mastery_score,

        "xp":
        profile.xp if profile else 0,
    }

@router.get("/progress")
def grammar_progress(
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):
    progress = (
        db.query(
            GrammarProgress
        )
        .filter(
            GrammarProgress.user_id
            == user_id
        )
        .all()
    )

    return progress