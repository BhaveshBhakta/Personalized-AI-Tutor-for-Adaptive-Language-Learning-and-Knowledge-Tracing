import json
import uuid

from sqlalchemy.orm import Session

from app.models.adaptive_exercise import (
    AdaptiveExercise,
)

from app.services.learner_state_service import (
    LearnerStateService,
)

from app.services.practice_queue_service import (
    PracticeQueueService,
)

from app.services.llm_service import (
    LLMService,
)


class AdaptiveExerciseService:


    def __init__(self):

        self.learner_state = (
            LearnerStateService()
        )

        self.practice_queue = (
            PracticeQueueService()
        )

        self.llm = (
            LLMService()
        )


    def _choose_difficulty(

        self,

        mastery_probability: float,

        confidence: float,

    ) -> int:


        if confidence < 0.30:

            return 2


        if mastery_probability < 0.25:

            return 1


        if mastery_probability < 0.45:

            return 2


        if mastery_probability < 0.65:

            return 3


        if mastery_probability < 0.80:

            return 4


        return 5


    def _find_mastery(

        self,

        state: dict,

        category: str,

        topic: str,

    ) -> tuple[float, float]:


        normalized_category = (
            category
            .strip()
            .lower()
        )


        normalized_topic = (
            topic
            .strip()
            .lower()
        )


        for item in state.get(

            "topic_mastery",

            [],

        ):


            item_category = (

                item["category"]
                .strip()
                .lower()

            )


            item_topic = (

                item["topic"]
                .strip()
                .lower()

            )


            if (

                item_category
                == normalized_category

                and item_topic
                == normalized_topic

            ):

                return (

                    float(
                        item[
                            "mastery_probability"
                        ]
                    ),

                    float(
                        item[
                            "confidence"
                        ]
                    ),

                )


        return (
            0.50,
            0.0,
        )


    def _clean_json_response(

        self,

        raw_response: str,

    ) -> dict:


        cleaned = (
            raw_response.strip()
        )


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


        return json.loads(
            cleaned.strip()
        )


    def generate_exercise(

        self,

        db: Session,

        user_id: int,

        provider: str = "groq",

    ) -> dict:


        queue = (

            self.practice_queue
            .build_queue(

                db=db,

                user_id=user_id,

                limit=5,

            )

        )


        state = (

            self.learner_state
            .get_state(

                db=db,

                user_id=user_id,

            )

        )


        if queue:

            target = queue[0]

            category = target[
                "category"
            ]

            topic = target[
                "topic"
            ]


        else:

            category = "general"

            topic = "German A1 practice"


        (
            mastery_probability,
            confidence,
        ) = self._find_mastery(

            state=state,

            category=category,

            topic=topic,

        )


        difficulty = (
            self._choose_difficulty(

                mastery_probability=
                    mastery_probability,

                confidence=
                    confidence,

            )
        )


        prompt = f"""
You generate adaptive German learning exercises.

Create exactly ONE exercise.

TARGET CATEGORY:
{category}

TARGET TOPIC:
{topic}

DIFFICULTY:
{difficulty} out of 5

LEARNER MASTERY:
{mastery_probability:.2f}

MASTERY CONFIDENCE:
{confidence:.2f}

Allowed exercise types:

- multiple_choice
- fill_blank
- translation
- correction

Difficulty:

1 = simple recognition
2 = basic recall
3 = contextual application
4 = production and deeper application
5 = subtle advanced distinction

Return valid JSON only:

{{
    "exercise_type": "multiple_choice",
    "question": "Question text",
    "options": [
        {{
            "id": "a",
            "text": "Option A"
        }},
        {{
            "id": "b",
            "text": "Option B"
        }},
        {{
            "id": "c",
            "text": "Option C"
        }},
        {{
            "id": "d",
            "text": "Option D"
        }}
    ],
    "correct_answer": "a",
    "explanation": "Clear educational explanation",
    "hint": "Short useful hint"
}}

Rules:

1. Generate only one exercise.

2. The exercise must genuinely test:
   {topic}

3. For multiple_choice:
   correct_answer must contain the option ID.

4. For fill_blank:
   correct_answer must contain the missing text.

5. For translation:
   correct_answer must contain one natural correct translation.

6. For correction:
   correct_answer must contain the corrected complete sentence.

7. For non-multiple-choice exercises:
   options must be null.

8. Do not use Markdown fences.

9. Do not write anything outside the JSON.
"""


        raw_response = (

            self.llm.ask(

                prompt=prompt,

                provider=provider,

            )

        )


        exercise_data = (
            self._clean_json_response(
                raw_response
            )
        )


        exercise_id = str(
            uuid.uuid4()
        )


        exercise = AdaptiveExercise(

            exercise_id=
                exercise_id,

            user_id=
                user_id,

            category=
                category,

            topic=
                topic,

            exercise_type=
                exercise_data[
                    "exercise_type"
                ],

            difficulty=
                difficulty,

            question=
                exercise_data[
                    "question"
                ],

            options=
                exercise_data.get(
                    "options"
                ),

            correct_answer=
                str(
                    exercise_data[
                        "correct_answer"
                    ]
                ),

            explanation=
                exercise_data[
                    "explanation"
                ],

            hint=
                exercise_data.get(
                    "hint"
                ),

            mastery_before=
                mastery_probability,

        )


        db.add(
            exercise
        )

        db.commit()

        db.refresh(
            exercise
        )


        return {

            "exercise_id":
                exercise.exercise_id,

            "category":
                exercise.category,

            "topic":
                exercise.topic,

            "exercise_type":
                exercise.exercise_type,

            "difficulty":
                exercise.difficulty,

            "question":
                exercise.question,

            "options":
                exercise.options,

            "hint":
                exercise.hint,

            "metadata": {

                "mastery_before":
                    exercise.mastery_before,

                "confidence":
                    confidence,

            },

        }


    def get_stored_exercise(

        self,

        db: Session,

        exercise_id: str,

        user_id: int,

    ) -> AdaptiveExercise | None:


        return (

            db.query(
                AdaptiveExercise
            )

            .filter(

                AdaptiveExercise.exercise_id
                == exercise_id,

                AdaptiveExercise.user_id
                == user_id,

            )

            .first()

        )