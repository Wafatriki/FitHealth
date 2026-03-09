from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://fithealth:changeme@db:5432/fithealth_db"
    APP_NAME: str = "FitHealth API"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
