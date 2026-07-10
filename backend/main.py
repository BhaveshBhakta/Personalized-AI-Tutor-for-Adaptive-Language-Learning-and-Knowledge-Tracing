from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.vocabulary import router as vocabulary_router
from app.api.flashcards import router as flashcard_router
from app.api.dashboard import router as dashboard_router
from app.api.german_words import router as german_words_router
from app.api.grammar import router as grammar_router
from app.api.planner import router as planner_router
from app.api.intelligence import router as intelligence_router
from app.api.vocabulary_intelligence import (router as vocabulary_intelligence_router,)
from app.api.documents import router as document_router
from app.api.ai import router as ai_router
from app.api.exercises import (router as exercises_router,)
from app.api.mastery import (router as mastery_router,)
from app.api.adaptive_exercises import (router as adaptive_exercises_router,)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(vocabulary_router)
app.include_router(flashcard_router)
app.include_router(dashboard_router)
app.include_router(german_words_router)
app.include_router(grammar_router)
app.include_router(planner_router)
app.include_router(intelligence_router)
app.include_router(vocabulary_intelligence_router)
app.include_router(document_router)
app.include_router(ai_router)
app.include_router(exercises_router)
app.include_router(mastery_router)
app.include_router(adaptive_exercises_router)

@app.get("/")
def root():
    return {
        "status": "ok"
    }