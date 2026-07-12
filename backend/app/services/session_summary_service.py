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

from app.services.learner_state_service import (
    LearnerStateService,
)


class SessionSummaryService:

    def __init__(self):

        self.learner_state = (
            LearnerStateService()
        )

    def build_summary(

        self,

        db: Session,

        user_id: int,

        session_id: int,

    ) -> dict:

        session = (

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

        if not session:

            raise ValueError(
                "Practice session not found"
            )

        items = (

            db.query(
                PracticeSessionItem
            )

            .filter(

                PracticeSessionItem.session_id
                == session.id,

            )

            .all()

        )

        total = len(items)

        correct = sum(

            1

            for item in items

            if item.is_correct

        )

        average_score = (

            sum(

                item.score or 0

                for item in items

            )

            / total

            if total

            else 0

        )

        improved_topics = []

        weak_topics = []

        for item in items:

            exercise = (

                db.query(
                    AdaptiveExercise
                )

                .filter(

                    AdaptiveExercise.id
                    == item.exercise_id

                )

                .first()

            )

            if not exercise:

                continue

            if item.is_correct:

                improved_topics.append(
                    exercise.topic
                )

            else:

                weak_topics.append(
                    exercise.topic
                )

        improved_topics = list(
            dict.fromkeys(
                improved_topics
            )
        )

        weak_topics = list(
            dict.fromkeys(
                weak_topics
            )
        )

        learner_state = (

            self.learner_state
            .get_state(

                db=db,

                user_id=user_id,

            )

        )

        recommendations = []

        for weakness in learner_state.get(

            "recurring_weaknesses",

            [],

        )[:3]:

            recommendations.append(

                {

                    "category":
                        weakness["category"],

                    "topic":
                        weakness["topic"],

                }

            )

        return {

            "session_id":
                session.id,

            "accuracy":

                round(

                    (
                        correct
                        / total
                    )
                    * 100,

                    1,

                )

                if total

                else 0,

            "correct":
                correct,

            "incorrect":
                total - correct,

            "average_score":
                round(
                    average_score,
                    2,
                ),

            "improved_topics":
                improved_topics,

            "weak_topics":
                weak_topics,

            "recommendations":
                recommendations,

        }