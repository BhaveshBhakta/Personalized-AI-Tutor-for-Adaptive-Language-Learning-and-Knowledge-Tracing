from sqlalchemy import func

from sqlalchemy.orm import Session

from app.models.adaptive_exercise import (
    AdaptiveExercise,
)

from app.models.exercise_attempt import (
    ExerciseAttempt,
)


class DifficultyService:


    LEVELS = [
        "A1",
        "A2",
        "B1",
        "B2",
    ]


    def get_topic_difficulty(

        self,

        db: Session,

        user_id: int,

        topic: str,

        default_level: str,

    ) -> str:


        recent_attempts = (

            db.query(
                ExerciseAttempt
            )

            .join(
                AdaptiveExercise,

                ExerciseAttempt.exercise_id
                == AdaptiveExercise.id,
            )

            .filter(

                ExerciseAttempt.user_id
                == user_id,

                AdaptiveExercise.topic
                == topic,

            )

            .order_by(

                ExerciseAttempt.created_at.desc()

            )

            .limit(5)

            .all()

        )


        if not recent_attempts:

            return default_level


        average_score = (

            sum(

                attempt.score

                for attempt
                in recent_attempts

            )

            / len(
                recent_attempts
            )

        )


        try:

            current_index = (
                self.LEVELS.index(
                    default_level
                )
            )

        except ValueError:

            current_index = 0


        if (

            len(recent_attempts) >= 3

            and average_score >= 0.85

        ):

            return self.LEVELS[

                min(

                    current_index + 1,

                    len(self.LEVELS) - 1,

                )

            ]


        if (

            len(recent_attempts) >= 2

            and average_score < 0.40

        ):

            return self.LEVELS[

                max(

                    current_index - 1,

                    0,

                )

            ]


        return default_level