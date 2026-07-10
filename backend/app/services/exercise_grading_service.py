import json

from sqlalchemy import func

from sqlalchemy.orm import Session

from app.models.exercise_attempt import (
    ExerciseAttempt,
)

from app.services.adaptive_exercise_service import (
    AdaptiveExerciseService,
)

from app.services.learning_signal_service import (
    LearningSignalService,
)

from app.services.knowledge_tracing_service import (
    KnowledgeTracingService,
)

from app.services.llm_service import (
    LLMService,
)


class ExerciseGradingService:


    def __init__(

        self,

        exercise_service:
            AdaptiveExerciseService,

    ):

        self.exercise_service = (
            exercise_service
        )

        self.signal_service = (
            LearningSignalService()
        )

        self.knowledge_tracer = (
            KnowledgeTracingService()
        )

        self.llm = (
            LLMService()
        )


    def _normalize(

        self,

        value: str,

    ) -> str:


        return (

            " ".join(
                value
                .strip()
                .lower()
                .split()
            )

        )


    def _grade_exact(

        self,

        submitted: str,

        expected: str,

    ) -> tuple[
        bool,
        float,
        str,
    ]:


        is_correct = (

            self._normalize(
                submitted
            )

            ==

            self._normalize(
                expected
            )

        )


        return (

            is_correct,

            1.0 if is_correct else 0.0,

            "exact",

        )


    def _grade_with_llm(

        self,

        question: str,

        submitted: str,

        expected: str,

        exercise_type: str,

        provider: str,

    ) -> tuple[
        bool,
        float,
        str,
    ]:


        prompt = f"""
Grade a German language exercise answer.

EXERCISE TYPE:
{exercise_type}

QUESTION:
{question}

REFERENCE ANSWER:
{expected}

LEARNER ANSWER:
{submitted}

Judge semantic and grammatical correctness.

For translation exercises:
accept natural equivalent translations even when wording differs.

For correction exercises:
accept equivalent correct sentence structures when they preserve
the required meaning and grammatical target.

For fill-in-the-blank:
be stricter about the required grammatical form.

Return JSON only:

{{
    "is_correct": true,
    "score": 1.0
}}

Score must be between 0.0 and 1.0.

Do not include Markdown.
Do not include explanations.
"""


        raw = (

            self.llm.ask(

                prompt=prompt,

                provider=provider,

            )

        )


        cleaned = raw.strip()


        if cleaned.startswith(
            "```json"
        ):

            cleaned = cleaned[7:]


        elif cleaned.startswith(
            "```"
        ):

            cleaned = cleaned[3:]


        if cleaned.endswith(
            "```"
        ):

            cleaned = cleaned[:-3]


        result = json.loads(
            cleaned.strip()
        )


        score = float(
            result.get(
                "score",
                0.0,
            )
        )


        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )


        is_correct = bool(
            result.get(
                "is_correct",
                score >= 0.8,
            )
        )


        return (

            is_correct,

            score,

            "llm_semantic",

        )


    def grade_answer(

        self,

        db: Session,

        user_id: int,

        exercise_id: str,

        answer: str,

        provider: str = "groq",

    ) -> dict:


        exercise = (

            self.exercise_service
            .get_stored_exercise(

                db=db,

                exercise_id=
                    exercise_id,

                user_id=user_id,

            )

        )


        if not exercise:

            raise ValueError(
                "Exercise not found"
            )


        attempt_count = (

            db.query(
                func.count(
                    ExerciseAttempt.id
                )
            )

            .filter(

                ExerciseAttempt.exercise_id
                == exercise.id,

                ExerciseAttempt.user_id
                == user_id,

            )

            .scalar()

            or 0

        )


        attempt_number = (
            attempt_count + 1
        )


        if exercise.exercise_type in {

            "multiple_choice",
            "fill_blank",

        }:

            (
                is_correct,
                score,
                grading_method,
            ) = self._grade_exact(

                submitted=answer,

                expected=
                    exercise.correct_answer,

            )


        else:

            (
                is_correct,
                score,
                grading_method,
            ) = self._grade_with_llm(

                question=
                    exercise.question,

                submitted=
                    answer,

                expected=
                    exercise.correct_answer,

                exercise_type=
                    exercise.exercise_type,

                provider=
                    provider,

            )


        attempt = ExerciseAttempt(

            exercise_id=
                exercise.id,

            user_id=
                user_id,

            submitted_answer=
                answer,

            is_correct=
                is_correct,

            score=
                score,

            attempt_number=
                attempt_number,

            grading_method=
                grading_method,

        )


        db.add(
            attempt
        )

        db.commit()

        db.refresh(
            attempt
        )


        affected_topics = (

            self.signal_service
            .record_exercise_result(

                db=db,

                user_id=user_id,

                category=
                    exercise.category,

                topic=
                    exercise.topic,

                is_correct=
                    is_correct,

                score=
                    score,

                attempt_number=
                    attempt_number,

            )

        )


        for category, topic in (
            affected_topics
        ):

            self.knowledge_tracer \
                .calculate_topic_mastery(

                    db=db,

                    user_id=user_id,

                    category=category,

                    topic=topic,

                )


        if is_correct:

            next_action = (
                "increase_difficulty"
            )


        elif attempt_number >= 2:

            next_action = (
                "show_remediation"
            )


        else:

            next_action = (
                "reinforce_topic"
            )


        return {

            "exercise_id":
                exercise.exercise_id,

            "is_correct":
                is_correct,

            "score":
                score,

            "correct_answer":
                exercise.correct_answer,

            "explanation":
                exercise.explanation,

            "category":
                exercise.category,

            "topic":
                exercise.topic,

            "difficulty":
                exercise.difficulty,

            "attempt_number":
                attempt_number,

            "grading_method":
                grading_method,

            "next_action":
                next_action,

        }