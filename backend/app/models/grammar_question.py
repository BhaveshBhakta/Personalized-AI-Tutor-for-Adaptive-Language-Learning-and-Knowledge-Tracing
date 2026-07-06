from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base_class import Base


class GrammarQuestion(Base):
    __tablename__ = "grammar_questions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey(
            "grammar_topics.id"
        )
    )

    question: Mapped[str] = mapped_column(
        String(500)
    )

    option_a: Mapped[str] = mapped_column(
        String(100)
    )

    option_b: Mapped[str] = mapped_column(
        String(100)
    )

    option_c: Mapped[str] = mapped_column(
        String(100)
    )

    correct_answer: Mapped[str] = mapped_column(
        String(100)
    )