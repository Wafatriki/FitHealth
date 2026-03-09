from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.workout import WorkoutCreate, WorkoutRead, WorkoutUpdate

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("/user/{user_id}", response_model=list[WorkoutRead])
def list_user_workouts(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.workout.get_workouts_by_user(db, user_id=user_id, skip=skip, limit=limit)


@router.post("/user/{user_id}", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(user_id: int, workout_data: WorkoutCreate, db: Session = Depends(get_db)):
    if not crud.user.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return crud.workout.create_workout(db, workout_data, user_id=user_id)


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = crud.workout.get_workout(db, workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return db_workout


@router.patch("/{workout_id}", response_model=WorkoutRead)
def update_workout(workout_id: int, workout_data: WorkoutUpdate, db: Session = Depends(get_db)):
    db_workout = crud.workout.update_workout(db, workout_id, workout_data)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return db_workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    if not crud.workout.delete_workout(db, workout_id):
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
