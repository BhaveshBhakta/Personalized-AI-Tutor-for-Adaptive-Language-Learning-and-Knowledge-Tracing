from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class TopicMastery(Base):

    __tablename__ = "topic_mastery"

    __table_args__ = (

        UniqueConstraint(

            "user_id",
            "category",
            "topic",

            name="uq_topic_mastery_user_category_topic",

        ),

    )


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

    skill_id: Mapped[int | None] = mapped_column(

        ForeignKey(
            "skills.id",
            ondelete="SET NULL",
        ),

        nullable=True,

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


    mastery_probability: Mapped[float] = mapped_column(
        Float,
        default=0.30,
        nullable=False,
    )


    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )


    evidence_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    correct_evidence: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    incorrect_evidence: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    last_evidence_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True,
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )