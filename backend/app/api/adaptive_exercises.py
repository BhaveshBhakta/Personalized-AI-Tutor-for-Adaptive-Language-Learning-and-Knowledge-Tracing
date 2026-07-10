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

from app.schemas.adaptive_exercise import (
    ExerciseAnswerRequest,
)

from app.services.adaptive_exercise_service import (
    AdaptiveExerciseService,
)

from app.services.exercise_grading_service import (
    ExerciseGradingService,
)


router = APIRouter(

    prefix="/adaptive-exercises",

    tags=[
        "Adaptive Exercises"
    ],

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


@router.post("/next")
def next_exercise(

    provider: str = "groq",

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    try:

        return (

            exercise_service
            .generate_exercise(

                db=db,

                user_id=user_id,

                provider=provider,

            )

        )


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Failed to generate exercise: "
                + str(error)
            ),

        )


@router.post("/answer")
def answer_exercise(

    data: ExerciseAnswerRequest,

    provider: str = "groq",

    db: Session = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),

):


    try:

        return (

            grading_service
            .grade_answer(

                db=db,

                user_id=user_id,

                exercise_id=
                    data.exercise_id,

                answer=
                    data.answer,

                provider=
                    provider,

            )

        )


    except ValueError as error:

        raise HTTPException(

            status_code=404,

            detail=str(
                error
            ),

        )