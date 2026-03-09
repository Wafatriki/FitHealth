from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate


def get_workout(db: Session, workout_id: int) -> Workout | None:
    return db.query(Workout).filter(Workout.id == workout_id).first()


def get_workouts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Workout]:
    return db.query(Workout).filter(Workout.user_id == user_id).offset(skip).limit(limit).all()


def create_workout(db: Session, workout_data: WorkoutCreate, user_id: int) -> Workout:
    db_workout = Workout(**workout_data.model_dump(), user_id=user_id)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


def update_workout(db: Session, workout_id: int, workout_data: WorkoutUpdate) -> Workout | None:
    db_workout = get_workout(db, workout_id)
    if not db_workout:
        return None
    for field, value in workout_data.model_dump(exclude_unset=True).items():
        setattr(db_workout, field, value)
    db.commit()
    db.refresh(db_workout)
    return db_workout


def delete_workout(db: Session, workout_id: int) -> bool:
    db_workout = get_workout(db, workout_id)
    if not db_workout:
        return False
    db.delete(db_workout)
    db.commit()
    return True
