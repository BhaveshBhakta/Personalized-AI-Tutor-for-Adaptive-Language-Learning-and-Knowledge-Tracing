from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class PracticeSessionItem(Base):

    __tablename__ = "practice_session_items"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "practice_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    exercise_id: Mapped[int] = mapped_column(
        ForeignKey(
            "adaptive_exercises.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )


    answered: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )


    is_correct: Mapped[
        bool | None
    ] = mapped_column(
        nullable=True,
    )


    score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )