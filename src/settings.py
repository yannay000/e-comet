# type: ignore

from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):

    # for development
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")

class ClickHouseSettings(BaseSettings):
    CLICKHOUSE_HOST: AnyHttpUrl = Field(..., env="CLICKHOUSE_HOST")
    CLICKHOUSE_DATABASE: str = Field(..., env="CLICKHOUSE_DATABASE")

class ApiSettings(BaseSettings):
    SERVER_HOST: AnyHttpUrl = Field(..., env="SERVER_HOST")
    PROJECT_NAME: str = "e-c0met"
    DEBUG: bool = Field(default=True, env="DEBUG")
    DEBUG_PORT: int = 8080
    GITHUB_API_BASE_URL: AnyHttpUrl = Field(..., env="GITHUB_API_BASE_URL")
    OPENAPI_URL: str = Field(default="/openapi.json", env="OPENAPI_URL")

class Settings(
    DatabaseSettings,
    ApiSettings,
    ClickHouseSettings
):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
