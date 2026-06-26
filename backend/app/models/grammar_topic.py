from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class GrammarTopic(Base):
    __tablename__ = "grammar_topics"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )