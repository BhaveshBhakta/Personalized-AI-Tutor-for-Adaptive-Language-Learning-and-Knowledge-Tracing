from sqlalchemy.orm import Session

from app.models.learning_signal import (
    LearningSignal,
)

from app.models.topic_mastery import (
    TopicMastery,
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


        # -------------------------------------------------
        # BASE LEARNER CONTEXT
        # -------------------------------------------------

        base_context = (

            self.context_service
            .get_context(

                db=db,

                user_id=user_id,

            )

        )


        # -------------------------------------------------
        # LEARNING SIGNALS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # RECURRING WEAKNESSES
        # -------------------------------------------------

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


        # -------------------------------------------------
        # POSITIVE LEARNING SIGNALS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # UNIFIED TOPIC MASTERY
        # -------------------------------------------------

        topic_mastery_records = (

            db.query(
                TopicMastery
            )

            .filter(

                TopicMastery.user_id
                == user_id,

            )

            .order_by(

                TopicMastery
                .mastery_probability
                .asc(),

                TopicMastery
                .confidence
                .desc(),

            )

            .all()

        )


        topic_mastery = [

            {

                "skill_id":
                    record.skill_id,

                "category":
                    record.category,

                "topic":
                    record.topic,

                "mastery_probability":
                    record.mastery_probability,

                "confidence":
                    record.confidence,

                "evidence_count":
                    record.evidence_count,

                "correct_evidence":
                    record.correct_evidence,

                "incorrect_evidence":
                    record.incorrect_evidence,

            }

            for record
            in topic_mastery_records

        ]


        # -------------------------------------------------
        # LOW-MASTERY TOPICS
        # -------------------------------------------------

        weakest_mastery_topics = [

            item

            for item in topic_mastery

            if (

                item[
                    "mastery_probability"
                ] < 0.60

                and item[
                    "confidence"
                ] >= 0.20

            )

        ]


        # -------------------------------------------------
        # RETURN UNIFIED LEARNER STATE
        # -------------------------------------------------

        return {

            **base_context,

            "recurring_weaknesses":
                recurring_weaknesses,

            "positive_signals":
                positive_signals,

            "topic_mastery":
                topic_mastery,

            "weakest_mastery_topics":
                weakest_mastery_topics,

        }