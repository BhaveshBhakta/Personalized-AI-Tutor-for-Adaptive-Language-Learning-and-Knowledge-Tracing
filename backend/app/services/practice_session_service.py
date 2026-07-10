from sqlalchemy.orm import Session

from app.services.adaptive_exercise_service import (
    AdaptiveExerciseService,
)

from app.services.practice_queue_service import (
    PracticeQueueService,
)


class PracticeSessionService:


    def __init__(self):

        self.queue_service = (
            PracticeQueueService()
        )

        self.exercise_service = (
            AdaptiveExerciseService()
        )


    def create_session(

        self,

        db: Session,

        user_id: int,

        size: int = 5,

        provider: str = "groq",

    ) -> dict:


        size = max(
            1,
            min(
                size,
                10,
            ),
        )


        queue = (

            self.queue_service
            .build_queue(

                db=db,

                user_id=user_id,

                limit=size,

            )

        )


        exercises = []


        exercise_types = [

            "fill_blank",

            "multiple_choice",

            "translation",

            "correction",

        ]


        for index, target in enumerate(
            queue
        ):

            exercise_type = (

                exercise_types[

                    index
                    % len(exercise_types)

                ]

            )


            exercise = (

                self.exercise_service
                .generate(

                    db=db,

                    user_id=user_id,

                    exercise_type=
                        exercise_type,

                    provider=
                        provider,

                    target_override={
                        "category":
                            target["category"],

                        "topic":
                            target["topic"],

                        "reason":
                            target["reason"],
                    },

                )

            )


            exercises.append({

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

            })


        return {

            "exercise_count":
                len(exercises),

            "exercises":
                exercises,

        }