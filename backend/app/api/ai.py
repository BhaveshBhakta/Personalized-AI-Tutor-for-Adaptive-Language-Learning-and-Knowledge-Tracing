from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from app.core.auth import get_current_user_id
from app.services.ai_tutor import AITutor

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class Question(BaseModel):

    question: str

    provider: str = "groq"


tutor = AITutor()


@router.post("/ask")
def ask_ai(

    data: Question,

    user_id: int = Depends(
        get_current_user_id
    ),

):

    return tutor.ask(

        user_id=user_id,

        question=data.question,

        provider=data.provider,

    )