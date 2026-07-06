from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True
    )

    target_level: Mapped[str] = mapped_column(
        String(20),
        default="A1"
    )

    daily_goal_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    streak: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    user = relationship("User") 