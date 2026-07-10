from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base_class import Base


class AdaptiveExercise(Base):

    __tablename__ = "adaptive_exercises"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    exercise_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    topic: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )


    difficulty_level: Mapped[str] = mapped_column(
        String(20),
        default="A1",
        nullable=False,
    )


    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    expected_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    source_reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    attempts = relationship(
        "ExerciseAttempt",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )