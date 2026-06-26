"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the localization engine API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    supabase_url: str
    supabase_key: str
    supabase_service_key: str = ""
    anthropic_api_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    frontend_url: str = "http://localhost:3000"
    upload_dir: str = "uploads"

    @property
    def effective_supabase_key(self) -> str:
        """Prefer service role key for server-side operations when available."""
        return self.supabase_service_key or self.supabase_key


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
