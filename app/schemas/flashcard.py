from pydantic import BaseModel


class ReviewRequest(BaseModel):
    rating: str