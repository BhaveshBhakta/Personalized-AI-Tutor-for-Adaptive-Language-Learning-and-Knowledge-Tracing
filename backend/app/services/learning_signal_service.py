from sqlalchemy.orm import Session

from app.models.learning_signal import (
    LearningSignal,
)


class LearningSignalService:


    def record_signals(

        self,

        db: Session,

        user_id: int,

        conversation_id: int,

        signals: list[dict],

    ) -> None:


        for signal in signals:


            if signal[
                "confidence"
            ] < 0.65:

                continue


            existing = (

                db.query(
                    LearningSignal
                )

                .filter(

                    LearningSignal.user_id
                    == user_id,

                    LearningSignal.signal_type
                    == signal[
                        "signal_type"
                    ],

                    LearningSignal.category
                    == signal[
                        "category"
                    ],

                    LearningSignal.topic
                    == signal[
                        "topic"
                    ],

                )

                .first()

            )


            if existing:

                existing.occurrence_count += 1

                existing.confidence = max(

                    existing.confidence,

                    signal[
                        "confidence"
                    ],

                )

                existing.evidence = signal.get(
                    "evidence"
                )


            else:

                learning_signal = LearningSignal(

                    user_id=user_id,

                    conversation_id=
                        conversation_id,

                    signal_type=
                        signal["signal_type"],

                    category=
                        signal["category"],

                    topic=
                        signal["topic"],

                    evidence=
                        signal.get(
                            "evidence"
                        ),

                    confidence=
                        signal["confidence"],

                )

                db.add(
                    learning_signal
                )


        db.commit()

        def record_exercise_result(

            self,

            db: Session,

            user_id: int,

            category: str,

            topic: str,

            is_correct: bool,

            score: float,

            attempt_number: int,

        ) -> None:


            if is_correct and score >= 0.8:

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

                signal_type = (

                    "grammar_confusion"

                    if category == "grammar"

                    else "vocabulary_confusion"

                    if category == "vocabulary"

                    else "repeated_mistake"

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

                return


            self.record_signals(

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