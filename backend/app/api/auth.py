from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.models.user import User
from app.models.learning_profile import LearningProfile

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)

from app.core.security import (
    hash_password,
    verify_password,
)

from app.core.jwt import create_access_token
from app.db.dependencies import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):

    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    try:
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(
                data.password
            ),
        )

        db.add(user)

        # Obtain user.id without committing yet.
        db.flush()

        profile = LearningProfile(
            user_id=user.id,
            target_level="A1",
            daily_goal_minutes=30,
            xp=0,
            streak=0,
        )

        db.add(profile)

        # User and profile are committed together.
        db.commit()

        db.refresh(user)

        return {
            "message": "User created",
            "user_id": user.id,
        }

    except Exception:
        db.rollback()
        raise


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }