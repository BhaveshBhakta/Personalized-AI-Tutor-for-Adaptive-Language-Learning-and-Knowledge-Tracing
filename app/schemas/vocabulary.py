from pydantic import BaseModel


class VocabularyCreate(BaseModel):
    word: str
    article: str | None = None
    plural: str | None = None
    translation: str
    example_sentence: str | None = None


class VocabularyResponse(BaseModel):
    id: int
    word: str
    article: str | None = None
    plural: str | None = None
    translation: str
    example_sentence: str | None = None
    difficulty: int
    mastery_score: int

    class Config:
        from_attributes = True