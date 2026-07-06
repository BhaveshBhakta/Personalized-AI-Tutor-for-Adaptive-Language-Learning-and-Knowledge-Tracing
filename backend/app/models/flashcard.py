from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    vocabulary_id: Mapped[int] = mapped_column(
        ForeignKey("vocabulary.id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    review_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    mastery_score: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    stability: Mapped[float] = mapped_column(
        Float,
        default=1.0
    )

    difficulty: Mapped[float] = mapped_column(
        Float,
        default=5.0
    )

    retrievability: Mapped[float] = mapped_column(
        Float,
        default=1.0
    )

    interval_days: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    lapses: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    last_review: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    next_review: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    vocabulary = relationship(
        "Vocabulary"
    )

    user = relationship(
        "User"
    )