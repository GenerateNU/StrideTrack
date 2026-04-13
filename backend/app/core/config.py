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
    environment: str = "production"
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # OpenTelemetry
    otel_endpoint: str | None = Field(default=None, description="OTLP endpoint")

    # LLM
    llm_api_key: str = Field(..., description="API key for LiteLLM provider")
    llm_model: str = Field(
        default="openai/gpt-4o-mini", description="LiteLLM model string"
    )

    @property
    def debug(self) -> bool:
        """Debug mode enabled when environment is development."""
        return self.environment == "development"


settings = Settings()
