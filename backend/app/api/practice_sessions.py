from pydantic import BaseModel

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.auth import (
    get_current_user_id,
)

from app.db.dependencies import (
    get_db,
)

from app.services.practice_session_service import (
    PracticeSessionService,
)

from app.services.adaptive_exercise_service import (
    AdaptiveExerciseService,
)

from app.services.exercise_grading_service import (
    ExerciseGradingService,
)


router = APIRouter(

    prefix="/practice-sessions",

    tags=[
        "Practice Sessions"
    ],

)


session_service = (
    PracticeSessionService()
)


exercise_service = (
    AdaptiveExerciseService()
)


grading_service = (
    ExerciseGradingService(

        exercise_service=
            exercise_service

    )
)


class StartSessionRequest(BaseModel):

    target_exercises: int = 5

    provider: str = "groq"


class SessionAnswerRequest(BaseModel):

    exercise_id: str

    answer: str

    provider: str = "groq"


@router.post("/start")
def start_session(

    data: StartSessionRequest,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    try:

        return (

            session_service
            .start_session(

                db=db,

                user_id=user_id,

                target_exercises=
                    data.target_exercises,

                provider=
                    data.provider,

            )

        )


    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error),

        )


@router.get("/{session_id}")
def session_state(

    session_id: int,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    try:

        return (

            session_service
            .get_session_state(

                db=db,

                user_id=user_id,

                session_id=session_id,

            )

        )


    except ValueError as error:

        raise HTTPException(

            status_code=404,

            detail=str(error),

        )


@router.post(
    "/{session_id}/answer"
)
def answer_session_exercise(

    session_id: int,

    data: SessionAnswerRequest,

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    try:

        result = (

            grading_service
            .grade_answer(

                db=db,

                user_id=user_id,

                exercise_id=
                    data.exercise_id,

                answer=
                    data.answer,

                provider=
                    data.provider,

            )

        )


        session = (

            session_service
            .record_result(

                db=db,

                user_id=user_id,

                session_id=session_id,

                exercise_public_id=
                    data.exercise_id,

                result=result,

            )

        )


        next_exercise = None


        if session.status == "active":

            next_exercise = (

                session_service
                .create_next_exercise(

                    db=db,

                    user_id=user_id,

                    session_id=
                        session.id,

                    provider=
                        data.provider,

                )

            )


        average_score = (

            session.total_score
            / session.completed_exercises

            if session.completed_exercises > 0

            else 0.0

        )


        return {

            "result":
                result,

            "session": {

                "session_id":
                    session.id,

                "status":
                    session.status,

                "target_exercises":
                    session.target_exercises,

                "completed_exercises":
                    session.completed_exercises,

                "correct_exercises":
                    session.correct_exercises,

                "average_score":
                    average_score,

            },

            "next_exercise":
                next_exercise,

        }


    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error),

        )