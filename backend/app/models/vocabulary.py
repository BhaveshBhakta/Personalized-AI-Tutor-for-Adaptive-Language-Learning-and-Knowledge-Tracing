from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base_class import Base


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    word: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    article: Mapped[str] = mapped_column(
        String(10),
        nullable=True
    )

    plural: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    translation: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    example_sentence: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    difficulty: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    mastery_score: Mapped[int] = mapped_column(
        Integer,
        default=0
    )