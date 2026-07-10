from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.auth import (get_current_user_id,)
from app.db.dependencies import (get_db,)
from app.models.adaptive_exercise import (AdaptiveExercise,)
from app.services.adaptive_exercise_service import (AdaptiveExerciseService,)
from app.services.exercise_evaluator_service import (ExerciseEvaluatorService,)
from app.services.practice_session_service import (PracticeSessionService,)

router = APIRouter(
    prefix="/exercises",
    tags=["Adaptive Exercises"],
)

exercise_service = (
    AdaptiveExerciseService()
)

evaluator_service = (
    ExerciseEvaluatorService()
)

practice_session_service = (
    PracticeSessionService()
)

class PracticeSessionRequest(BaseModel):

    size: int = 5
    provider: str = "groq"

class GenerateExerciseRequest(BaseModel):

    exercise_type: str | None = None
    provider: str = "groq"


class SubmitAnswerRequest(BaseModel):

    answer: str
    provider: str = "groq"


@router.post("/generate")
def generate_exercise(

    data: GenerateExerciseRequest,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    try:

        exercise = (
            exercise_service.generate(

                db=db,
                user_id=user_id,
                exercise_type=
                    data.exercise_type,
                provider=
                    data.provider,

            )
        )

    except ValueError as exc:

        raise HTTPException(

            status_code=502,

            detail=str(exc),

        ) from exc

    return {

        "id":
            exercise.id,

        "exercise_type":
            exercise.exercise_type,

        "category":
            exercise.category,

        "topic":
            exercise.topic,

        "difficulty_level":
            exercise.difficulty_level,

        "question":
            exercise.question,

        "source_reason":
            exercise.source_reason,

    }

@router.post(
    "/{exercise_id}/submit"
)
def submit_answer(

    exercise_id: int,

    data: SubmitAnswerRequest,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    clean_answer = (
        data.answer.strip()
    )

    if not clean_answer:

        raise HTTPException(

            status_code=400,
            detail="Answer cannot be empty",

        )


    exercise = (

        db.query(
            AdaptiveExercise
        )

        .filter(

            AdaptiveExercise.id
            == exercise_id,

            AdaptiveExercise.user_id
            == user_id,

        )

        .first()

    )

    if not exercise:

        raise HTTPException(

            status_code=404,
            detail="Exercise not found",

        )

    try:

        attempt = (
            evaluator_service.evaluate(

                db=db,
                user_id=user_id,
                exercise=exercise,
                learner_answer=
                    clean_answer,
                provider=
                    data.provider,

            )
        )

    except ValueError as exc:

        raise HTTPException(

            status_code=502,
            detail=str(exc),

        ) from exc

    return {

        "exercise_id":
            exercise.id,

        "attempt_id":
            attempt.id,

        "attempt_number":
            attempt.attempt_number,

        "is_correct":
            attempt.is_correct,

        "score":
            attempt.score,

        "feedback":
            attempt.feedback,

        "expected_answer":
            exercise.expected_answer,

        "explanation":
            exercise.explanation,

    }

@router.post("/session")
def create_practice_session(

    data: PracticeSessionRequest,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    try:

        return (

            practice_session_service
            .create_session(

                db=db,
                user_id=user_id,
                size=data.size,
                provider=
                    data.provider,

            )
        )

    except ValueError as exc:

        raise HTTPException(

            status_code=502,
            detail=str(exc),

        ) from exc