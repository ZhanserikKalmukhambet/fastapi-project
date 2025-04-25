from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # main app
    APP_NAME: str = "OnAI Webhook Service"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # postgres
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_HOST: str
    POSTGRES_PORT: int 
    POSTGRES_DB: str 

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # redis
    REDIS_HOST: str 
    REDIS_PORT: int 
    REDIS_DB: int 

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # celery
    CELERY_URL: str 
    CELERY_RESULT_BACKEND: str 

    # openrouter
    OPENROUTER_API_KEY: str 
    OPENROUTER_BASE_URL: str 

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings() 