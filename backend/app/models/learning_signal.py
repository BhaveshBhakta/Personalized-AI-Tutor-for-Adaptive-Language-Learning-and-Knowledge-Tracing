from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class LearningSignal(Base):

    __tablename__ = "learning_signals"


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


    conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )


    signal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


    topic: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )


    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )


    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )