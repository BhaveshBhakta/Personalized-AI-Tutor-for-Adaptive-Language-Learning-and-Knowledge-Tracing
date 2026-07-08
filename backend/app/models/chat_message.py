from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base_class import Base


class ChatMessage(Base):

    __tablename__ = "chat_messages"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    conversation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )


    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    sources: Mapped[
        list[dict] | None
    ] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )