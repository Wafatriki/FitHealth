from datetime import datetime

from pydantic import BaseModel


class WorkoutCreate(BaseModel):
    name: str
    description: str | None = None
    duration_minutes: int
    calories_burned: int | None = None


class WorkoutRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    duration_minutes: int
    calories_burned: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    calories_burned: int | None = None
