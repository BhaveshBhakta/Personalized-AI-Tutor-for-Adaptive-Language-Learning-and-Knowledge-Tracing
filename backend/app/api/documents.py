from pathlib import Path
import shutil

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.dependencies import get_db

from app.models.document import Document

from app.services.document_processor import (
    DocumentProcessor,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path(
    "uploads/documents"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post("/upload")
async def upload_document(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    existing = (
        db.query(Document)
        .filter(
            Document.user_id == user_id,
            Document.filename == file.filename,
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Document already uploaded",
        )

    save_path = (
        UPLOAD_DIR /
        file.filename
    )

    with open(
        save_path,
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    extracted_text = (
        DocumentProcessor.extract_text(
            str(save_path)
        )
    )

    document = Document(

        user_id=user_id,

        filename=file.filename,

        filepath=str(save_path),

        text=extracted_text,

        status="processed",

    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return {

        "message":
        "Document uploaded successfully",

        "document_id":
        document.id,

        "filename":
        document.filename,

        "status":
        document.status,

        "characters":
        len(extracted_text),

    }


@router.get("/")
def list_documents(

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == user_id
        )
        .order_by(
            Document.uploaded_at.desc()
        )
        .all()
    )

    return documents


@router.get("/{document_id}")
def get_document(

    document_id: int,

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


@router.delete("/{document_id}")
def delete_document(

    document_id: int,

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user_id
    ),

):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(
        document.filepath
    )

    if file_path.exists():

        file_path.unlink()

    db.delete(document)

    db.commit()

    return {

        "message":
        "Document deleted successfully"

    }