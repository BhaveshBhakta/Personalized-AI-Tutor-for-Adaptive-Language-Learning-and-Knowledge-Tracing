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


        # -------------------------------------------------
        # PRIORITY 0
        # UNIFIED LOW-MASTERY TOPICS
        # -------------------------------------------------

        for weakness in state.get(

            "weakest_mastery_topics",

            [],

        ):


            category = (
                weakness["category"]
            )


            topic = (
                weakness["topic"]
            )


            key = (

                category.strip().lower(),

                topic.strip().lower(),

            )


            if key in seen:

                continue


            seen.add(
                key
            )


            queue.append({

                "category":
                    category,

                "topic":
                    topic,

                "reason":
                    "low_unified_mastery",

                "priority":
                    0,

                "mastery_probability":
                    weakness[
                        "mastery_probability"
                    ],

                "confidence":
                    weakness[
                        "confidence"
                    ],

                "evidence_count":
                    weakness.get(
                        "evidence_count",
                        0,
                    ),

            })


        # -------------------------------------------------
        # PRIORITY 1
        # RECURRING LEARNING DIFFICULTIES
        # -------------------------------------------------

        for weakness in state.get(

            "recurring_weaknesses",

            [],

        ):


            category = (
                weakness["category"]
            )


            topic = (
                weakness["topic"]
            )


            key = (

                category.strip().lower(),

                topic.strip().lower(),

            )


            if key in seen:

                continue


            seen.add(
                key
            )


            queue.append({

                "category":
                    category,

                "topic":
                    topic,

                "reason":
                    "recurring_learning_difficulty",

                "priority":
                    1,

                "confidence":
                    weakness.get(
                        "confidence"
                    ),

                "occurrences":
                    weakness.get(
                        "occurrences"
                    ),

            })


        # -------------------------------------------------
        # PRIORITY 2
        # WEAK GRAMMAR
        # -------------------------------------------------

        for grammar in state.get(

            "weak_grammar",

            [],

        ):


            topic = (

                grammar.get(
                    "title"
                )

                or grammar.get(
                    "topic"
                )

                or (

                    "Grammar topic "

                    + str(

                        grammar.get(

                            "topic_id",

                            "",

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

                "topic_id":
                    grammar.get(
                        "topic_id"
                    ),

                "mastery_score":
                    grammar.get(
                        "mastery_score"
                    ),

                "accuracy":
                    grammar.get(
                        "accuracy"
                    ),

            })


        # -------------------------------------------------
        # PRIORITY 3
        # WEAK VOCABULARY
        # -------------------------------------------------

        for vocabulary in state.get(

            "weak_vocabulary",

            [],

        ):


            topic = (
                vocabulary["word"]
            )


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

                "mastery_score":
                    vocabulary.get(
                        "mastery_score"
                    ),

                "retrievability":
                    vocabulary.get(
                        "retrievability"
                    ),

                "lapses":
                    vocabulary.get(
                        "lapses"
                    ),

            })


        # -------------------------------------------------
        # SORT QUEUE
        # -------------------------------------------------

        queue.sort(

            key=lambda item: (

                item[
                    "priority"
                ],

                item.get(
                    "mastery_probability",
                    1.0,
                ),

                -item.get(
                    "confidence",
                    0.0,
                ),

            )

        )


        # -------------------------------------------------
        # RETURN REQUESTED QUEUE SIZE
        # -------------------------------------------------

        return queue[:limit]