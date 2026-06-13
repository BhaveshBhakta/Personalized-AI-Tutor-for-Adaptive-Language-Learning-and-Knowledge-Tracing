from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.vocabulary import (
    router as vocabulary_router
)


app = FastAPI()

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(vocabulary_router)

@app.get("/")
def root():
    return {
        "status": "ok"
    }

