from sqlalchemy.orm import Session

from app.models.adaptive_exercise import (
    AdaptiveExercise,
)

from app.models.exercise_attempt import (
    ExerciseAttempt,
)

from app.models.learning_signal import (
    LearningSignal,
)


class MasteryEvidenceService:


    POSITIVE_SIGNALS = {

        "concept_understood",
        "correction_success",

    }


    NEGATIVE_SIGNALS = {

        "grammar_confusion",
        "vocabulary_confusion",
        "repeated_mistake",

    }


    def get_exercise_evidence(

        self,

        db: Session,

        user_id: int,

        category: str,

        topic: str,

        limit: int = 20,

    ) -> list[dict]:


        attempts = (

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

                AdaptiveExercise.category
                == category,

                AdaptiveExercise.topic
                == topic,

            )

            .order_by(

                ExerciseAttempt.created_at.desc()

            )

            .limit(limit)

            .all()

        )


        return [

            {

                "source":
                    "adaptive_exercise",

                "value":
                    float(
                        attempt.score
                    ),

                "weight":
                    1.0,

                "is_positive":
                    attempt.score >= 0.7,

                "created_at":
                    attempt.created_at,

            }

            for attempt in attempts

        ]


    def get_signal_evidence(

        self,

        db: Session,

        user_id: int,

        category: str,

        topic: str,

        limit: int = 20,

    ) -> list[dict]:


        signals = (

            db.query(
                LearningSignal
            )

            .filter(

                LearningSignal.user_id
                == user_id,

                LearningSignal.category
                == category,

                LearningSignal.topic
                == topic,

            )

            .order_by(

                LearningSignal.created_at.desc()

            )

            .limit(limit)

            .all()

        )


        evidence = []


        for signal in signals:


            if (
                signal.signal_type
                in self.POSITIVE_SIGNALS
            ):

                value = 1.0

                is_positive = True


            elif (
                signal.signal_type
                in self.NEGATIVE_SIGNALS
            ):

                value = 0.0

                is_positive = False


            else:

                continue


            evidence.append({

                "source":
                    "ai_learning_signal",

                "value":
                    value,

                "weight":
                    float(
                        signal.confidence
                    )
                    * min(
                        signal.occurrence_count,
                        3,
                    ),

                "is_positive":
                    is_positive,

                "created_at":
                    signal.created_at,

            })


        return evidence


    def collect_topic_evidence(

        self,

        db: Session,

        user_id: int,

        category: str,

        topic: str,

    ) -> list[dict]:


        evidence = []


        evidence.extend(

            self.get_exercise_evidence(

                db=db,

                user_id=user_id,

                category=category,

                topic=topic,

            )

        )


        evidence.extend(

            self.get_signal_evidence(

                db=db,

                user_id=user_id,

                category=category,

                topic=topic,

            )

        )


        evidence.sort(

            key=lambda item:
                item["created_at"],

            reverse=True,

        )


        return evidence