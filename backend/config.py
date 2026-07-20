from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Job Analyzer"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+psycopg2://user:pass@localhost:5432/ai_job_analyzer"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    UPLOAD_DIR: str = "uploads"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = {"env_file": ".env"}


settings = Settings()
