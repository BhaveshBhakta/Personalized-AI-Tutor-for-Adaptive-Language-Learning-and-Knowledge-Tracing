from sqlalchemy.orm import Session

from app.services.learner_state_service import (
    LearnerStateService,
)


class AdaptivePlanService:


    def __init__(self):

        self.learner_state = (
            LearnerStateService()
        )


    def build_plan(

        self,

        db: Session,

        user_id: int,

    ) -> dict:


        state = (

            self.learner_state
            .get_state(

                db=db,

                user_id=user_id,

            )

        )


        daily_minutes = state[
            "profile"
        ][
            "daily_goal_minutes"
        ]


        weaknesses = state[
            "recurring_weaknesses"
        ]


        weak_vocabulary = state[
            "weak_vocabulary"
        ]


        weak_grammar = state[
            "weak_grammar"
        ]


        tasks = []


        if weak_vocabulary:

            tasks.append({

                "type":
                    "vocabulary_review",

                "title":
                    "Review weak vocabulary",

                "minutes":
                    min(
                        10,
                        max(
                            5,
                            daily_minutes // 4,
                        ),
                    ),

                "priority":
                    "high",

                "reason":
                    "Low vocabulary recall",

                "items":
                    [
                        item["word"]

                        for item
                        in weak_vocabulary[:5]
                    ],

            })


        if weak_grammar:

            tasks.append({

                "type":
                    "grammar_practice",

                "title":
                    "Practice weak grammar",

                "minutes":
                    min(
                        15,
                        max(
                            5,
                            daily_minutes // 3,
                        ),
                    ),

                "priority":
                    "high",

                "reason":
                    "Low grammar mastery",

                "topic_ids":
                    [

                        item["topic_id"]

                        for item
                        in weak_grammar[:3]

                    ],

            })


        if weaknesses:

            top_weakness = weaknesses[0]


            tasks.append({

                "type":
                    "ai_tutor_practice",

                "title":
                    (
                        "Practice "
                        + top_weakness[
                            "topic"
                        ]
                    ),

                "minutes":
                    min(
                        10,
                        max(
                            5,
                            daily_minutes // 4,
                        ),
                    ),

                "priority":
                    "high",

                "reason":
                    "Recurring learning difficulty",

                "topic":
                    top_weakness[
                        "topic"
                    ],

            })


        used_minutes = sum(

            task["minutes"]

            for task in tasks

        )


        remaining_minutes = max(

            0,

            daily_minutes
            - used_minutes,

        )


        if remaining_minutes > 0:

            tasks.append({

                "type":
                    "general_practice",

                "title":
                    "General German practice",

                "minutes":
                    remaining_minutes,

                "priority":
                    "normal",

                "reason":
                    "Daily learning consistency",

            })


        return {

            "daily_goal_minutes":
                daily_minutes,

            "tasks":
                tasks,

            "adaptive":
                True,

        }