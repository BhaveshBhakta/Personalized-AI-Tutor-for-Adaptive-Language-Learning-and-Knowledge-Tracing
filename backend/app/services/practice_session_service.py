from datetime import datetime

from sqlalchemy.orm import Session

from app.models.practice_session import (
    PracticeSession,
)

from app.models.practice_session_item import (
    PracticeSessionItem,
)

from app.models.adaptive_exercise import (
    AdaptiveExercise,
)

from app.services.adaptive_exercise_service import (
    AdaptiveExerciseService,
)


class PracticeSessionService:


    def __init__(self):

        self.exercise_service = (
            AdaptiveExerciseService()
        )


    def start_session(

        self,

        db: Session,

        user_id: int,

        target_exercises: int = 5,

        provider: str = "groq",

    ) -> dict:


        target_exercises = max(

            1,

            min(
                target_exercises,
                20,
            ),

        )


        active_session = (

            db.query(
                PracticeSession
            )

            .filter(

                PracticeSession.user_id
                == user_id,

                PracticeSession.status
                == "active",

            )

            .order_by(

                PracticeSession.started_at.desc()

            )

            .first()

        )


        if active_session:

            return self.get_session_state(

                db=db,

                user_id=user_id,

                session_id=
                    active_session.id,

            )


        session = PracticeSession(

            user_id=user_id,

            status="active",

            target_exercises=
                target_exercises,

        )


        db.add(session)

        db.commit()

        db.refresh(session)


        exercise_data = (

            self.exercise_service
            .generate_exercise(

                db=db,

                user_id=user_id,

                provider=provider,

            )

        )


        exercise = (

            db.query(
                AdaptiveExercise
            )

            .filter(

                AdaptiveExercise.exercise_id
                == exercise_data[
                    "exercise_id"
                ],

                AdaptiveExercise.user_id
                == user_id,

            )

            .first()

        )


        if not exercise:

            session.status = "failed"

            db.commit()

            raise ValueError(
                "Generated exercise could not be found"
            )


        item = PracticeSessionItem(

            session_id=session.id,

            exercise_id=exercise.id,

            sequence_number=1,

        )


        db.add(item)

        db.commit()


        return {

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

            "exercise":
                exercise_data,

        }


    def get_session(

        self,

        db: Session,

        user_id: int,

        session_id: int,

    ) -> PracticeSession | None:


        return (

            db.query(
                PracticeSession
            )

            .filter(

                PracticeSession.id
                == session_id,

                PracticeSession.user_id
                == user_id,

            )

            .first()

        )


    def get_current_item(

        self,

        db: Session,

        session_id: int,

    ) -> PracticeSessionItem | None:


        return (

            db.query(
                PracticeSessionItem
            )

            .filter(

                PracticeSessionItem.session_id
                == session_id,

                PracticeSessionItem.answered
                == False,

            )

            .order_by(

                PracticeSessionItem.sequence_number.asc()

            )

            .first()

        )


    def get_session_state(

        self,

        db: Session,

        user_id: int,

        session_id: int,

    ) -> dict:


        session = self.get_session(

            db=db,

            user_id=user_id,

            session_id=session_id,

        )


        if not session:

            raise ValueError(
                "Practice session not found"
            )


        current_item = (

            self.get_current_item(

                db=db,

                session_id=session.id,

            )

        )


        exercise_data = None


        if current_item:

            exercise = (

                db.query(
                    AdaptiveExercise
                )

                .filter(

                    AdaptiveExercise.id
                    == current_item.exercise_id

                )

                .first()

            )


            if exercise:

                exercise_data = {

                    "exercise_id":
                        exercise.exercise_id,

                    "category":
                        exercise.category,

                    "topic":
                        exercise.topic,

                    "exercise_type":
                        exercise.exercise_type,

                    "difficulty":
                        exercise.difficulty,

                    "question":
                        exercise.question,

                    "options":
                        exercise.options,

                    "hint":
                        exercise.hint,

                    "metadata": {

                        "mastery_before":
                            exercise.mastery_before,

                    },

                }


        average_score = (

            session.total_score
            / session.completed_exercises

            if session.completed_exercises > 0

            else 0.0

        )


        return {

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

            "exercise":
                exercise_data,

        }


    def record_result(

        self,

        db: Session,

        user_id: int,

        session_id: int,

        exercise_public_id: str,

        result: dict,

    ) -> PracticeSession:


        session = self.get_session(

            db=db,

            user_id=user_id,

            session_id=session_id,

        )


        if not session:

            raise ValueError(
                "Practice session not found"
            )


        if session.status != "active":

            raise ValueError(
                "Practice session is not active"
            )


        exercise = (

            db.query(
                AdaptiveExercise
            )

            .filter(

                AdaptiveExercise.exercise_id
                == exercise_public_id,

                AdaptiveExercise.user_id
                == user_id,

            )

            .first()

        )


        if not exercise:

            raise ValueError(
                "Exercise not found"
            )


        item = (

            db.query(
                PracticeSessionItem
            )

            .filter(

                PracticeSessionItem.session_id
                == session.id,

                PracticeSessionItem.exercise_id
                == exercise.id,

            )

            .first()

        )


        if not item:

            raise ValueError(
                "Exercise does not belong to this session"
            )


        if item.answered:

            raise ValueError(
                "Exercise already answered"
            )


        item.answered = True

        item.is_correct = result[
            "is_correct"
        ]

        item.score = result[
            "score"
        ]


        session.completed_exercises += 1

        session.total_score += float(
            result["score"]
        )


        if result["is_correct"]:

            session.correct_exercises += 1


        if (

            session.completed_exercises
            >= session.target_exercises

        ):

            session.status = "completed"

            session.completed_at = (
                datetime.utcnow()
            )


        db.commit()

        db.refresh(session)


        return session


    def create_next_exercise(

        self,

        db: Session,

        user_id: int,

        session_id: int,

        provider: str = "groq",

    ) -> dict | None:


        session = self.get_session(

            db=db,

            user_id=user_id,

            session_id=session_id,

        )


        if not session:

            raise ValueError(
                "Practice session not found"
            )


        if session.status == "completed":

            return None


        existing_item = (

            self.get_current_item(

                db=db,

                session_id=session.id,

            )

        )


        if existing_item:

            return self.get_session_state(

                db=db,

                user_id=user_id,

                session_id=session.id,

            )["exercise"]


        exercise_data = (

            self.exercise_service
            .generate_exercise(

                db=db,

                user_id=user_id,

                provider=provider,

            )

        )


        exercise = (

            db.query(
                AdaptiveExercise
            )

            .filter(

                AdaptiveExercise.exercise_id
                == exercise_data[
                    "exercise_id"
                ],

                AdaptiveExercise.user_id
                == user_id,

            )

            .first()

        )


        if not exercise:

            raise ValueError(
                "Generated exercise could not be found"
            )


        next_sequence = (

            session.completed_exercises
            + 1

        )


        item = PracticeSessionItem(

            session_id=
                session.id,

            exercise_id=
                exercise.id,

            sequence_number=
                next_sequence,

        )


        db.add(item)

        db.commit()


        return exercise_data