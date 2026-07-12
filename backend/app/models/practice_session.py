from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class PracticeSession(Base):

    __tablename__ = "practice_sessions"


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


    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
        index=True,
    )


    target_exercises: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )


    completed_exercises: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    correct_exercises: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    total_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )


    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True,
    )