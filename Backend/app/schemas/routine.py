from datetime import datetime

from pydantic import BaseModel


# --- Routine Exercise ---
class RoutineExerciseCreate(BaseModel):
    name: str
    sets: int | None = None
    reps: int | None = None
    duration_minutes: int | None = None
    notes: str | None = None


class RoutineExerciseRead(BaseModel):
    id: int
    routine_id: int
    name: str
    sets: int | None
    reps: int | None
    duration_minutes: int | None
    notes: str | None

    model_config = {"from_attributes": True}


# --- Routine Diet ---
class RoutineDietCreate(BaseModel):
    name: str
    description: str | None = None
    calories: int | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    notes: str | None = None


class RoutineDietRead(BaseModel):
    id: int
    routine_id: int
    name: str
    description: str | None
    calories: int | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    notes: str | None

    model_config = {"from_attributes": True}


# --- Routine ---
class RoutineCreate(BaseModel):
    name: str
    description: str | None = None
    exercises: list[RoutineExerciseCreate] = []
    diet_items: list[RoutineDietCreate] = []


class RoutineRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    created_at: datetime
    exercises: list[RoutineExerciseRead] = []
    diet_items: list[RoutineDietRead] = []

    model_config = {"from_attributes": True}


class RoutineUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
