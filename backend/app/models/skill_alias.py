from sqlalchemy import (
    ForeignKey,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base_class import Base


class SkillAlias(Base):

    __tablename__ = "skill_aliases"


    __table_args__ = (

        UniqueConstraint(

            "normalized_alias",
            "category",

            name=(
                "uq_skill_alias_category"
            ),

        ),

    )


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    skill_id: Mapped[int] = mapped_column(

        ForeignKey(
            "skills.id",
            ondelete="CASCADE",
        ),

        nullable=False,

        index=True,

    )


    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )


    alias: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    normalized_alias: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )