from jose import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from app.core.config import settings

security = HTTPBearer()


def get_current_user_id(
    token=Depends(security)
):
    print("========== AUTH DEBUG ==========")
    print("Raw token:", token.credentials)

    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        print("Decoded payload:", payload)

        return int(payload["sub"])

    except Exception as e:
        print("JWT ERROR:", repr(e))

        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )