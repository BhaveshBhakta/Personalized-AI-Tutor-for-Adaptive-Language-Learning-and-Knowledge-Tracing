from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.vocabulary import (router as vocabulary_router)
from app.api.flashcards import (router as flashcard_router)
from app.api.dashboard import (router as dashboard_router)
from app.api.german_words import (router as german_words_router)
from app.api.grammar import (router as grammar_router)
from app.api.planner import (router as planner_router)

app = FastAPI()

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(vocabulary_router)
app.include_router(flashcard_router)
app.include_router(dashboard_router)
app.include_router(german_words_router)
app.include_router(grammar_router)
app.include_router(planner_router)

@app.get("/")
def root():
    return {
        "status": "ok"
    }

