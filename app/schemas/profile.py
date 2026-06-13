from pydantic import BaseModel


class ProfileCreate(BaseModel):
    target_level: str
    daily_goal_minutes: int


class ProfileResponse(BaseModel):
    target_level: str
    daily_goal_minutes: int
    xp: int
    streak: int