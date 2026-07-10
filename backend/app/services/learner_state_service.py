from sqlalchemy.orm import Session

from app.models.learning_signal import (
    LearningSignal,
)

from app.services.learner_context_service import (
    LearnerContextService,
)


class LearnerStateService:


    def __init__(self):

        self.context_service = (
            LearnerContextService()
        )


    def get_state(

        self,

        db: Session,

        user_id: int,

    ) -> dict:


        base_context = (

            self.context_service
            .get_context(

                db=db,

                user_id=user_id,

            )

        )


        signals = (

            db.query(
                LearningSignal
            )

            .filter(

                LearningSignal.user_id
                == user_id,

                LearningSignal.confidence
                >= 0.65,

            )

            .order_by(

                LearningSignal.occurrence_count.desc(),

                LearningSignal.confidence.desc(),

            )

            .limit(20)

            .all()

        )


        recurring_weaknesses = [

            {

                "type":
                    signal.signal_type,

                "category":
                    signal.category,

                "topic":
                    signal.topic,

                "confidence":
                    signal.confidence,

                "occurrences":
                    signal.occurrence_count,

            }

            for signal in signals

            if signal.signal_type in {

                "grammar_confusion",
                "vocabulary_confusion",
                "repeated_mistake",

            }

        ]


        positive_signals = [

            {

                "type":
                    signal.signal_type,

                "category":
                    signal.category,

                "topic":
                    signal.topic,

                "confidence":
                    signal.confidence,

                "occurrences":
                    signal.occurrence_count,

            }

            for signal in signals

            if signal.signal_type in {

                "correction_success",
                "concept_understood",

            }

        ]


        return {

            **base_context,

            "recurring_weaknesses":
                recurring_weaknesses,

            "positive_signals":
                positive_signals,

        }