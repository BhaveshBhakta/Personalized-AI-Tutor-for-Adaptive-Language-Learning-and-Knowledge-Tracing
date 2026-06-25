from pydantic import BaseModel


class DocumentChunkResponse(
    BaseModel
):

    id: int

    chunk_index: int

    content: str

    class Config:

        from_attributes = True  