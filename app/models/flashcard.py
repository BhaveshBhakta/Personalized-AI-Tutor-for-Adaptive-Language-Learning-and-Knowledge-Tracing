from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from app.db.base import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    vocabulary_id = Column(
        Integer,
        ForeignKey("vocabulary.id"),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    review_count = Column(
        Integer,
        default=0,
    )

    mastery_score = Column(
        Integer,
        default=0,
    )

    stability = Column(
        Float,
        default=1.0,
    )

    difficulty = Column(
        Float,
        default=5.0,
    )

    retrievability = Column(
        Float,
        default=1.0,
    )

    interval_days = Column(
        Integer,
        default=0,
    )

    lapses = Column(
        Integer,
        default=0,
    )

    last_review = Column(
        DateTime,
        default=datetime.utcnow,
    )

    next_review = Column(
        DateTime,
        default=datetime.utcnow,
    )