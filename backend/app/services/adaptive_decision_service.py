from sqlalchemy.orm import Session

from app.services.learner_state_service import (
    LearnerStateService,
)


class AdaptiveDecisionService:

    def __init__(self):

        self.learner_state = (
            LearnerStateService()
        )

    def next_learning_action(

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

        recurring = state.get(
            "recurring_weaknesses",
            [],
        )

        if recurring:

            weakness = recurring[0]

            return {

                "action":
                    "practice",

                "reason":
                    "recurring_weakness",

                "category":
                    weakness["category"],

                "topic":
                    weakness["topic"],

                "difficulty":
                    2,

            }

        mastery = state.get(
            "weakest_mastery_topics",
            [],
        )

        if mastery:

            weakest = mastery[0]

            difficulty = 2

            if weakest[
                "mastery_probability"
            ] < 0.25:

                difficulty = 1

            return {

                "action":
                    "practice",

                "reason":
                    "low_mastery",

                "category":
                    weakest["category"],

                "topic":
                    weakest["topic"],

                "difficulty":
                    difficulty,

            }

        vocab = state.get(
            "weak_vocabulary",
            [],
        )

        if vocab:

            return {

                "action":
                    "flashcards",

                "reason":
                    "weak_vocabulary",

                "topic":
                    vocab[0]["word"],

            }
        
        grammar = state.get(
            "weak_grammar",
            [],
        )

        if grammar:

            return {

                "action":
                    "grammar",

                "reason":
                    "weak_grammar",

                "topic":
                    grammar[0]["title"],

            }

        return {

            "action":
                "general_practice",

            "reason":
                "continue_learning",

        }