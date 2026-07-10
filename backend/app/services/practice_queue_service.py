from sqlalchemy.orm import Session

from app.services.learner_state_service import (
    LearnerStateService,
)


class PracticeQueueService:


    def __init__(self):

        self.learner_state = (
            LearnerStateService()
        )


    def build_queue(

        self,

        db: Session,

        user_id: int,

        limit: int = 5,

    ) -> list[dict]:


        state = (

            self.learner_state
            .get_state(

                db=db,

                user_id=user_id,

            )

        )


        queue = []

        seen = set()


        for weakness in state.get(
            "recurring_weaknesses",
            [],
        ):

            key = (

                weakness["category"],

                weakness["topic"]
                .strip()
                .lower(),

            )


            if key in seen:

                continue


            seen.add(
                key
            )


            queue.append({

                "category":
                    weakness["category"],

                "topic":
                    weakness["topic"],

                "reason":
                    "recurring_learning_difficulty",

                "priority":
                    1,

            })


        for grammar in state.get(
            "weak_grammar",
            [],
        ):

            topic = (

                grammar.get("title")

                or grammar.get("topic")

                or (
                    "Grammar topic "
                    + str(
                        grammar.get(
                            "topic_id",
                            ""
                        )
                    )
                )

            )


            key = (
                "grammar",
                topic.strip().lower(),
            )


            if key in seen:

                continue


            seen.add(
                key
            )


            queue.append({

                "category":
                    "grammar",

                "topic":
                    topic,

                "reason":
                    "low_grammar_mastery",

                "priority":
                    2,

            })


        for vocabulary in state.get(
            "weak_vocabulary",
            [],
        ):

            topic = vocabulary[
                "word"
            ]


            key = (
                "vocabulary",
                topic.strip().lower(),
            )


            if key in seen:

                continue


            seen.add(
                key
            )


            queue.append({

                "category":
                    "vocabulary",

                "topic":
                    topic,

                "reason":
                    "low_vocabulary_mastery",

                "priority":
                    3,

            })


        queue.sort(

            key=lambda item:
                item["priority"]

        )


        return queue[:limit]