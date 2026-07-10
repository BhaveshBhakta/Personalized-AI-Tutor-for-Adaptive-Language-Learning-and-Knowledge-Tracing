import json

from sqlalchemy.orm import Session
from app.models.adaptive_exercise import (AdaptiveExercise,)
from app.services.learner_state_service import (LearnerStateService,)
from app.services.llm_service import (LLMService,)
from app.services.difficulty_service import (DifficultyService,)

class AdaptiveExerciseService:

    ALLOWED_TYPES = {

        "multiple_choice",
        "fill_blank",
        "translation",
        "correction",

    }

    def __init__(self):

        self.learner_state = (
            LearnerStateService()
        )

        self.llm = (
            LLMService()
        )

        self.difficulty_service = (
            DifficultyService()
        )

    def select_target(

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

        recurring_weaknesses = state.get(
            "recurring_weaknesses",
            [],
        )

        weak_grammar = state.get(
            "weak_grammar",
            [],
        )

        weak_vocabulary = state.get(
            "weak_vocabulary",
            [],
        )

        if recurring_weaknesses:

            weakness = (
                recurring_weaknesses[0]
            )

            return {

                "category":
                    weakness["category"],

                "topic":
                    weakness["topic"],

                "reason":
                    "recurring_learning_difficulty",

            }

        if weak_grammar:

            grammar = weak_grammar[0]

            return {

                "category":
                    "grammar",

                "topic":
                    grammar.get(
                        "title",
                        grammar.get(
                            "topic",
                            "German grammar",
                        ),
                    ),

                "reason":
                    "low_grammar_mastery",

            }

        if weak_vocabulary:

            vocabulary = (
                weak_vocabulary[0]
            )

            return {

                "category":
                    "vocabulary",

                "topic":
                    vocabulary["word"],

                "reason":
                    "low_vocabulary_mastery",

            }

        return {

            "category":
                "general",

            "topic":
                "A1 German fundamentals",

            "reason":
                "general_practice",

        }

    def generate(

        self,

        db: Session,

        user_id: int,

        exercise_type: str | None = None,

        provider: str = "groq",

        target_override: dict | None = None,

    ) -> AdaptiveExercise:

        state = (

            self.learner_state
            .get_state(

                db=db,
                user_id=user_id,

            )
        )

        target = (

            target_override

            if target_override

            else self.select_target(

                db=db,

                user_id=user_id,

            )

        )

        profile = state.get(
            "profile",
            {},
        )

        level = profile.get(
            "target_level",
            "A1",
        )

        level = (

            self.difficulty_service
            .get_topic_difficulty(

                db=db,

                user_id=user_id,

                topic=
                    target["topic"],

                default_level=
                    level,

            )

        )

        selected_type = (

            exercise_type
            if exercise_type
            in self.ALLOWED_TYPES
            else "fill_blank"

        )

        prompt = f"""
You generate one German language learning exercise.

Learner level:
{level}

Target category:
{target["category"]}

Target topic:
{target["topic"]}

Exercise type:
{selected_type}

Return ONLY valid JSON in exactly this structure:

{{
  "exercise_type": "{selected_type}",
  "category": "{target["category"]}",
  "topic": "{target["topic"]}",
  "question": "exercise question here",
  "expected_answer": "correct answer here",
  "explanation": "short educational explanation"
}}

Rules:

1. Generate exactly one exercise.

2. Match the learner's level.

3. Test the target topic directly.

4. The expected answer must be clear enough for automatic
   or AI-assisted evaluation.

5. Do not include the answer inside the question.

6. For fill_blank, use exactly one clear blank written as _____.

7. For translation exercises, clearly state the translation direction.

8. For correction exercises, provide one incorrect German sentence.

9. Keep the exercise focused on one learning objective.

10. Return JSON only.
"""

        raw_response = self.llm.ask(

            prompt=prompt,
            provider=provider,

        )

        try:

            data = json.loads(
                raw_response
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Exercise generator returned invalid JSON"
            ) from exc


        question = str(
            data.get(
                "question",
                "",
            )
        ).strip()

        expected_answer = str(
            data.get(
                "expected_answer",
                "",
            )
        ).strip()

        explanation = str(
            data.get(
                "explanation",
                "",
            )
        ).strip()

        if not question:

            raise ValueError(
                "Generated exercise has no question"
            )

        if not expected_answer:

            raise ValueError(
                "Generated exercise has no expected answer"
            )

        exercise = AdaptiveExercise(

            user_id=user_id,

            exercise_type=
                selected_type,

            category=
                target["category"],

            topic=
                target["topic"],

            difficulty_level=
                level,

            question=
                question,

            expected_answer=
                expected_answer,

            explanation=
                explanation,

            source_reason=
                target["reason"],

        )

        db.add(exercise)
        db.commit()
        db.refresh(exercise)

        return exercise