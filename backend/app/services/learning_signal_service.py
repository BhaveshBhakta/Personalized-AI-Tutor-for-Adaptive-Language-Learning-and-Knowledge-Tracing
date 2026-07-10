from sqlalchemy.orm import Session

from app.models.learning_signal import (
    LearningSignal,
)


class LearningSignalService:


    def record_signals(

        self,

        db: Session,

        user_id: int,

        conversation_id: int | None,

        signals: list[dict],

    ) -> list[tuple[str, str]]:


        affected_topics: set[
            tuple[str, str]
        ] = set()


        for signal in signals:


            confidence = signal.get(
                "confidence",
                0.0,
            )


            if confidence < 0.65:

                continue


            signal_type = signal.get(
                "signal_type"
            )


            category = signal.get(
                "category"
            )


            topic = signal.get(
                "topic"
            )


            if not signal_type:

                continue


            if not category:

                continue


            if not topic:

                continue


            category = (
                category
                .strip()
                .lower()
            )


            topic = topic.strip()


            if not topic:

                continue


            affected_topics.add(

                (
                    category,
                    topic,
                )

            )


            existing = (

                db.query(
                    LearningSignal
                )

                .filter(

                    LearningSignal.user_id
                    == user_id,

                    LearningSignal.signal_type
                    == signal_type,

                    LearningSignal.category
                    == category,

                    LearningSignal.topic
                    == topic,

                )

                .first()

            )


            if existing:


                existing.occurrence_count += 1


                existing.confidence = max(

                    existing.confidence,

                    confidence,

                )


                existing.evidence = signal.get(
                    "evidence"
                )


                if conversation_id is not None:

                    existing.conversation_id = (
                        conversation_id
                    )


            else:


                learning_signal = (
                    LearningSignal(

                        user_id=
                            user_id,

                        conversation_id=
                            conversation_id,

                        signal_type=
                            signal_type,

                        category=
                            category,

                        topic=
                            topic,

                        evidence=
                            signal.get(
                                "evidence"
                            ),

                        confidence=
                            confidence,

                    )
                )


                db.add(
                    learning_signal
                )


        db.commit()


        return list(
            affected_topics
        )


    def record_exercise_result(

        self,

        db: Session,

        user_id: int,

        category: str,

        topic: str,

        is_correct: bool,

        score: float,

        attempt_number: int,

    ) -> list[tuple[str, str]]:


        if (
            is_correct
            and score >= 0.8
        ):


            signal_type = (
                "concept_understood"
            )


            confidence = min(

                0.95,

                0.70
                + (
                    attempt_number
                    * 0.05
                ),

            )


            evidence = (

                "Successful adaptive "
                "exercise attempt."

            )


        elif score < 0.5:


            if category == "grammar":

                signal_type = (
                    "grammar_confusion"
                )


            elif category == "vocabulary":

                signal_type = (
                    "vocabulary_confusion"
                )


            else:

                signal_type = (
                    "repeated_mistake"
                )


            confidence = min(

                0.95,

                0.70
                + (
                    attempt_number
                    * 0.05
                ),

            )


            evidence = (

                "Low score on adaptive "
                "exercise."

            )


        else:

            return []


        return self.record_signals(

            db=db,

            user_id=user_id,

            conversation_id=None,

            signals=[

                {

                    "signal_type":
                        signal_type,

                    "category":
                        category,

                    "topic":
                        topic,

                    "evidence":
                        evidence,

                    "confidence":
                        confidence,

                }

            ],

        )