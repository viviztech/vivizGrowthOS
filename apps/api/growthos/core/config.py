from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    app_name: str = "VIVIZ GrowthOS API"
    environment: str = "development"
    secret_key: str = Field(default="development-only-change-this-secret-key", min_length=32)
    access_token_minutes: int = 60
    database_url: str = "postgresql+asyncpg://growthos:growthos@localhost:5432/growthos"
    redis_url: str = "redis://localhost:6379/0"
    api_cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
