from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5438/auditchain_db"
    secret_key: str = "dev"
    public_key: str = "dev"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database_url = self.database_url.strip()
        self.secret_key = self.secret_key.strip()
        self.public_key = self.public_key.strip()
        self.algorithm = self.algorithm.strip()
        self.environment = self.environment.strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()
