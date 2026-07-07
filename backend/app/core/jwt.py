from datetime import datetime
from datetime import timedelta

from jose import jwt

from app.core.config import settings


def create_access_token(
    user_id: int
) -> str:

    expire = (
        datetime.utcnow()
        + timedelta(minutes=15)
    )


    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }


    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(
    user_id: int
) -> str:

    expire = (
        datetime.utcnow()
        + timedelta(days=30)
    )


    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
    }


    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )