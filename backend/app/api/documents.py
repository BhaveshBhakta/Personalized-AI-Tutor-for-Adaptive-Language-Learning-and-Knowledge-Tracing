from pathlib import Path

import shutil


from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)


from sqlalchemy.orm import Session


from app.core.auth import (
    get_current_user_id,
)


from app.db.dependencies import (
    get_db,
)


from app.models.document import (
    Document,
)


from app.models.document_chunk import (
    DocumentChunk,
)


from app.services.document_processor import (
    DocumentProcessor,
)


from app.services.text_chunker import (
    TextChunker,
)


from app.services.vector_store import (
    VectorStore,
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


vector_store = VectorStore()


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

            detail=(
                "Only PDF files are allowed"
            ),

        )


    existing = (

        db.query(Document)

        .filter(

            Document.user_id
            == user_id,

            Document.filename
            == file.filename,

        )

        .first()

    )


    if existing:

        raise HTTPException(

            status_code=400,

            detail=(
                "Document already uploaded"
            ),

        )


    user_directory = (

        UPLOAD_DIR
        / str(user_id)

    )


    user_directory.mkdir(

        parents=True,

        exist_ok=True,

    )


    save_path = (

        user_directory
        / file.filename

    )


    try:

        with open(
            save_path,
            "wb",
        ) as buffer:

            shutil.copyfileobj(

                file.file,

                buffer,

            )


        extracted_text = (

            DocumentProcessor
            .extract_text(
                str(save_path)
            )

        )


        if not extracted_text.strip():

            if save_path.exists():

                save_path.unlink()


            raise HTTPException(

                status_code=400,

                detail=(
                    "No readable text was found in the PDF"
                ),

            )


        document = Document(

            user_id=user_id,

            filename=file.filename,

            filepath=str(save_path),

            text=extracted_text,

            status="processing",

        )


        db.add(document)

        db.commit()

        db.refresh(document)


        chunks = (

            TextChunker.chunk_text(

                text=extracted_text,

                chunk_size=500,

                overlap=100,

            )

        )


        for index, content in enumerate(
            chunks
        ):

            db_chunk = DocumentChunk(

                document_id=
                    document.id,

                chunk_index=
                    index,

                content=
                    content,

            )


            db.add(db_chunk)


        db.commit()


        vector_store.add_document_chunks(

            user_id=user_id,

            document_id=
                document.id,

            filename=
                document.filename,

            chunks=chunks,

        )


        document.status = "processed"

        db.commit()

        db.refresh(document)


        return {

            "message":
                "Document uploaded and indexed successfully",

            "document_id":
                document.id,

            "filename":
                document.filename,

            "status":
                document.status,

            "characters":
                len(extracted_text),

            "chunks":
                len(chunks),

        }


    except HTTPException:

        raise


    except Exception as error:

        db.rollback()


        if save_path.exists():

            save_path.unlink()


        raise HTTPException(

            status_code=500,

            detail=(
                f"Document processing failed: {str(error)}"
            ),

        )


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

            Document.user_id
            == user_id

        )

        .order_by(

            Document.uploaded_at.desc()

        )

        .all()

    )


    return [

        {

            "id":
                document.id,

            "filename":
                document.filename,

            "status":
                document.status,

            "uploaded_at":
                document.uploaded_at,

        }

        for document in documents

    ]


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

            Document.id
            == document_id,

            Document.user_id
            == user_id,

        )

        .first()

    )


    if not document:

        raise HTTPException(

            status_code=404,

            detail=(
                "Document not found"
            ),

        )


    chunk_count = (

        db.query(DocumentChunk)

        .filter(

            DocumentChunk.document_id
            == document.id

        )

        .count()

    )


    return {

        "id":
            document.id,

        "filename":
            document.filename,

        "status":
            document.status,

        "uploaded_at":
            document.uploaded_at,

        "characters":
            len(document.text or ""),

        "chunks":
            chunk_count,

    }


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

            Document.id
            == document_id,

            Document.user_id
            == user_id,

        )

        .first()

    )


    if not document:

        raise HTTPException(

            status_code=404,

            detail=(
                "Document not found"
            ),

        )


    vector_store.delete_document(

        user_id=user_id,

        document_id=
            document.id,

    )


    db.query(DocumentChunk).filter(

        DocumentChunk.document_id
        == document.id

    ).delete()


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