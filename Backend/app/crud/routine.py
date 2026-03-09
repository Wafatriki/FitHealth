from sqlalchemy.orm import Session

from app.models.routine import Routine, RoutineExercise, RoutineDiet
from app.schemas.routine import RoutineCreate, RoutineUpdate


def get_routine(db: Session, routine_id: int) -> Routine | None:
    return db.query(Routine).filter(Routine.id == routine_id).first()


def get_routines_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Routine]:
    return db.query(Routine).filter(Routine.user_id == user_id).offset(skip).limit(limit).all()


def create_routine(db: Session, routine_data: RoutineCreate, user_id: int) -> Routine:
    db_routine = Routine(
        user_id=user_id,
        name=routine_data.name,
        description=routine_data.description,
    )
    for ex in routine_data.exercises:
        db_routine.exercises.append(RoutineExercise(**ex.model_dump()))
    for di in routine_data.diet_items:
        db_routine.diet_items.append(RoutineDiet(**di.model_dump()))
    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)
    return db_routine


def update_routine(db: Session, routine_id: int, routine_data: RoutineUpdate) -> Routine | None:
    db_routine = get_routine(db, routine_id)
    if not db_routine:
        return None
    for field, value in routine_data.model_dump(exclude_unset=True).items():
        setattr(db_routine, field, value)
    db.commit()
    db.refresh(db_routine)
    return db_routine


def delete_routine(db: Session, routine_id: int) -> bool:
    db_routine = get_routine(db, routine_id)
    if not db_routine:
        return False
    db.delete(db_routine)
    db.commit()
    return True
