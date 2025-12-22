from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Supabase
    supabase_url: str = Field(..., description="Supabase URL")
    supabase_service_role_key: str = Field(
        ..., description="Secret key to access supabase"
    )

    # App
    app_name: str = "StrideTrack API"
    debug: bool = False
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # OpenTelemetry
    otel_endpoint: str | None = Field(default=None, description="OTLP endpoint")


settings = Settings()
