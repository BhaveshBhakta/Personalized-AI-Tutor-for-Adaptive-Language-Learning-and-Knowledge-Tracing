from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):

    id: int

    filename: str

    status: str

    uploaded_at: datetime

    class Config:
        from_attributes = True