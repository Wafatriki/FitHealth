from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.routine import RoutineCreate, RoutineRead, RoutineUpdate

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("/", response_model=list[RoutineRead])
def list_my_routines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.routine.get_routines_by_user(db, current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=RoutineRead, status_code=status.HTTP_201_CREATED)
def create_routine(
    routine_data: RoutineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.routine.create_routine(db, routine_data, user_id=current_user.id)


@router.get("/{routine_id}", response_model=RoutineRead)
def get_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_routine = crud.routine.get_routine(db, routine_id)
    if not db_routine or db_routine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return db_routine


@router.patch("/{routine_id}", response_model=RoutineRead)
def update_routine(
    routine_id: int,
    routine_data: RoutineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_routine = crud.routine.get_routine(db, routine_id)
    if not db_routine or db_routine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    return crud.routine.update_routine(db, routine_id, routine_data)


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_routine = crud.routine.get_routine(db, routine_id)
    if not db_routine or db_routine.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    crud.routine.delete_routine(db, routine_id)
