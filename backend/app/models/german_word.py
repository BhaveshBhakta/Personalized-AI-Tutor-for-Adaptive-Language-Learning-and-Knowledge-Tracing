from sqlalchemy import String
from sqlalchemy import Integer

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base_class import Base


class GermanWord(Base):
    __tablename__ = "german_words"

    id: Mapped[int] = mapped_column(
        primary_key=True
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

    category: Mapped[str] = mapped_column(
        String(100),
        default="General"
    )

    difficulty: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    frequency_rank: Mapped[int] = mapped_column(
        Integer,
        default=9999
    )