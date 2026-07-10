from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class Skill(Base):

    __tablename__ = "skills"


    __table_args__ = (

        UniqueConstraint(

            "skill_key",

            name="uq_skill_key",

        ),

    )


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    skill_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )


    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    level: Mapped[str] = mapped_column(
        String(10),
        default="A1",
        nullable=False,
    )


    parent_skill_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )