from pydantic import BaseModel


class GermanWordResponse(BaseModel):
    id: int
    word: str
    article: str | None = None
    plural: str | None = None
    translation: str
    category: str
    difficulty: int
    frequency_rank: int

    class Config:
        from_attributes = True