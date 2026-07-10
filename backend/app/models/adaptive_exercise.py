from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class AdaptiveExercise(Base):

    __tablename__ = "adaptive_exercises"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    exercise_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )


    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    exercise_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


    difficulty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )


    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    options: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )


    correct_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    hint: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    mastery_before: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )