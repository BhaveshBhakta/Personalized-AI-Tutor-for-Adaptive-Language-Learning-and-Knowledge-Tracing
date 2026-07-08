from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.dependencies import get_db
from app.models.document import Document
from app.services.memory_service import MemoryService
from app.services.ai_orchestrator import AIOrchestrator
from app.models.conversation import Conversation

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


memory = MemoryService()
orchestrator = AIOrchestrator()


class Question(BaseModel):
    question: str
    provider: str = "groq"
    conversation_id: int | None = None
    document_ids: list[int] | None = None


class ConversationCreate(BaseModel):
    provider: str = "groq"

class ConversationUpdate(BaseModel):
    title: str

def validate_documents(
    db: Session,
    user_id: int,
    document_ids: list[int] | None,
):
    if not document_ids:
        return

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == user_id,
            Document.id.in_(document_ids),
        )
        .all()
    )

    found_ids = {
        document.id
        for document in documents
    }

    requested_ids = set(document_ids)

    if found_ids != requested_ids:
        raise HTTPException(
            status_code=404,
            detail="One or more selected documents were not found",
        )


@router.post("/conversations")
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    conversation = memory.create_conversation(
        db=db,
        user_id=user_id,
        provider=data.provider,
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "provider": conversation.provider,
        "created_at": conversation.created_at,
    }


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    conversations = memory.list_conversations(
        db=db,
        user_id=user_id,
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "provider": conversation.provider,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.get(
    "/conversations/{conversation_id}/messages"
)
def conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    conversation = memory.get_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return memory.get_history(
        db=db,
        conversation_id=conversation_id,
        limit=100,
    )

@router.delete(
    "/conversations/{conversation_id}"
)
def delete_conversation(

    conversation_id: int,

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    deleted = (

        memory.delete_conversation(

            db=db,

            user_id=user_id,

            conversation_id=
                conversation_id,

        )

    )


    if not deleted:

        raise HTTPException(

            status_code=404,

            detail=(
                "Conversation not found"
            ),

        )


    return {

        "message":
            "Conversation deleted successfully",

        "conversation_id":
            conversation_id,

    }

@router.post("/ask")
def ask_ai(
    data: Question,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    validate_documents(
        db=db,
        user_id=user_id,
        document_ids=data.document_ids,
    )

    if data.conversation_id:
        conversation = memory.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=data.conversation_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

    else:
        conversation = memory.create_conversation(
            db=db,
            user_id=user_id,
            provider=data.provider,
        )

    result = orchestrator.ask(
        db=db,
        user_id=user_id,
        conversation_id=conversation.id,
        question=data.question,
        provider=data.provider,
        document_ids=data.document_ids,
    )

    memory.update_title_from_question(
        db=db,
        conversation=conversation,
        question=data.question,
    )

    return {
        **result,
        "conversation_id": conversation.id,
    }


@router.post("/stream")
def stream_ai(
    data: Question,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    validate_documents(
        db=db,
        user_id=user_id,
        document_ids=data.document_ids,
    )

    if data.conversation_id:
        conversation = memory.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=data.conversation_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

    else:
        conversation = memory.create_conversation(
            db=db,
            user_id=user_id,
            provider=data.provider,
        )

    memory.update_title_from_question(
        db=db,
        conversation=conversation,
        question=data.question,
    )

    response = StreamingResponse(
        orchestrator.stream_answer(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            question=data.question,
            provider=data.provider,
            document_ids=data.document_ids,
        ),
        media_type="text/plain",
    )

    response.headers["X-Conversation-ID"] = str(
        conversation.id
    )

    return response

@router.patch(
    "/conversations/{conversation_id}"
)
def rename_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_current_user_id
    ),
):

    clean_title = data.title.strip()


    if not clean_title:

        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty",
        )


    if len(clean_title) > 200:

        raise HTTPException(
            status_code=400,
            detail=(
                "Title cannot exceed "
                "200 characters"
            ),
        )


    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id
            == conversation_id,

            Conversation.user_id
            == user_id,
        )
        .first()
    )


    if not conversation:

        raise HTTPException(
            status_code=404,
            detail=(
                "Conversation not found"
            ),
        )


    conversation.title = (
        clean_title
    )


    db.commit()

    db.refresh(
        conversation
    )


    return {
        "id":
            conversation.id,

        "title":
            conversation.title,

        "provider":
            conversation.provider,

        "updated_at":
            conversation.updated_at,
    }