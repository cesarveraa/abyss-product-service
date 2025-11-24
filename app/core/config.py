from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "inventory-product-service"
    API_V1_STR: str = "/api/v1"

    # Supabase / Postgres
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Auth
    JWT_SECRET: str
    COOKIE_NAME: str = "session"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
