"""Configuration settings for the application."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # OpenAI
    openai_api_key: str
    
    # Database
    database_url: str
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "ytblog"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # YouTube
    youtube_api_key: str = ""
    
    # SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@example.com"
    
    # App
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    api_v1_prefix: str = "/api/v1"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
