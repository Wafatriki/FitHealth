from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[EventRead])
def list_my_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.event.get_events_by_user(db, current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.event.create_event(db, event_data, user_id=current_user.id)


@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_event = crud.event.get_event(db, event_id)
    if not db_event or db_event.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return db_event


@router.patch("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_event = crud.event.get_event(db, event_id)
    if not db_event or db_event.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return crud.event.update_event(db, event_id, event_data)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_event = crud.event.get_event(db, event_id)
    if not db_event or db_event.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    crud.event.delete_event(db, event_id)
