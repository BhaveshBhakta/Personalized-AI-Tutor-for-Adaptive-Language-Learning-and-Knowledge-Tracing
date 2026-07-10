from typing import Any

from pydantic import (
    BaseModel,
    Field,
)


class ExerciseOption(BaseModel):

    id: str

    text: str


class GeneratedExercise(BaseModel):

    exercise_id: str

    category: str

    topic: str

    exercise_type: str

    difficulty: int = Field(
        ge=1,
        le=5,
    )

    question: str

    options: list[
        ExerciseOption
    ] | None = None

    hint: str | None = None

    metadata: dict[
        str,
        Any,
    ] = {}


class ExerciseAnswerRequest(BaseModel):

    exercise_id: str

    answer: str


class ExerciseAnswerResult(BaseModel):

    exercise_id: str

    is_correct: bool

    score: float

    correct_answer: str

    explanation: str

    category: str

    topic: str

    difficulty: int

    next_action: str