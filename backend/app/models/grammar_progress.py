from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base_class import Base


class GrammarProgress(Base):
    __tablename__ = "grammar_progress"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("grammar_topics.id"),
        nullable=False
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    total_answers: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    mastery_score: Mapped[int] = mapped_column(
        Integer,
        default=0
    )