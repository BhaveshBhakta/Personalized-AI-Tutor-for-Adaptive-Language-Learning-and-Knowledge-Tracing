from sqlalchemy.orm import Session

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response

from jose import JWTError
from jose import jwt

from app.core.config import settings
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

from app.core.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.core.jwt import create_access_token

from app.core.auth import (
    get_current_user_id,
)

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
        .filter(
            User.email == data.email
        )
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

        db.flush()


        profile = LearningProfile(
            user_id=user.id,
            target_level="A1",
            daily_goal_minutes=30,
            xp=0,
            streak=0,
        )


        db.add(profile)

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
    response: Response,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.email == data.email
        )
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


    access_token = (
        create_access_token(
            user.id
        )
    )


    refresh_token = (
        create_refresh_token(
            user.id
        )
    )


    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )


    return {
        "access_token":
            access_token,

        "token_type":
            "bearer",
    }

@router.get("/me")
def get_me(
    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),
):

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }

@router.post("/refresh")
def refresh_access_token(
    request: Request,
):

    refresh_token = (
        request.cookies.get(
            "refresh_token"
        )
    )


    if not refresh_token:

        raise HTTPException(
            status_code=401,
            detail="Refresh token missing",
        )


    try:

        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )


        if (
            payload.get("type")
            != "refresh"
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
            )


        user_id = int(
            payload.get("sub")
        )


    except (
        JWTError,
        ValueError,
        TypeError,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )


    new_access_token = (
        create_access_token(
            user_id
        )
    )


    return {
        "access_token":
            new_access_token,

        "token_type":
            "bearer",
    }

@router.post("/logout")
def logout(
    response: Response,
):

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )


    return {
        "message":
            "Logged out successfully"
    }