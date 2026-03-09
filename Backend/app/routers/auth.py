from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.auth import verify_password, create_access_token, get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if crud.user.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    if crud.user.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username ya registrado")
    if user_data.role not in ("patient", "doctor"):
        raise HTTPException(status_code=400, detail="Rol inválido")
    return crud.user.create_user(db, user_data)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = crud.user.get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
