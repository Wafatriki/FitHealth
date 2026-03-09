from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import users, workouts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas al arrancar (en producción usar Alembic en su lugar)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="API de FitHealth — seguimiento de entrenamientos y salud",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(workouts.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
