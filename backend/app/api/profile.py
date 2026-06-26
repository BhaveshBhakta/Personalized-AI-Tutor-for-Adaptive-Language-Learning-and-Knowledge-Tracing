from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.learning_profile import LearningProfile

from app.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
)

from app.core.auth import get_current_user_id

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.post("/")
def create_profile(
    data: ProfileCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    existing = (
        db.query(LearningProfile)
        .filter(LearningProfile.user_id == user_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists",
        )

    profile = LearningProfile(
        user_id=user_id,
        target_level=data.target_level,
        daily_goal_minutes=data.daily_goal_minutes,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "message": "Profile created",
        "profile_id": profile.id,
    }


@router.get(
    "/",
    response_model=ProfileResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    profile = (
        db.query(LearningProfile)
        .filter(LearningProfile.user_id == user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return ProfileResponse(
        target_level=profile.target_level,
        daily_goal_minutes=profile.daily_goal_minutes,
        xp=profile.xp,
        streak=profile.streak,
    )