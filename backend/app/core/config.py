from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Environment
    ENV: str = Field(default="development")
    API_DEBUG: bool = Field(default=True)

    # Clerk
    CLERK_JWKS_URL: str = Field(
        default="",
        description="Clerk JWKS URL, e.g., https://clerk.YOUR_DOMAIN/.well-known/jwks.json",
    )
    CLERK_ISSUER: Optional[str] = None
    CLERK_AUDIENCE: Optional[str] = None
    CLERK_WEBHOOK_SECRET: Optional[str] = None
    CLERK_SECRET_KEY: Optional[str] = None  # optional: not required for JWKS verification

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_BUCKET_UPLOADS: str = Field(default="uploads")

    # Admin
    ADMIN_USER_IDS: Optional[str] = Field(
        default=None, description="Comma-separated Clerk user IDs with admin access"
    )

    # CORS
    CORS_ORIGINS: Optional[str] = Field(
        default=None, description="Comma-separated list of allowed origins"
    )

    # Groq API Configuration
    GROQ_API_KEY: Optional[str] = Field(
        default=None, description="Groq API key for transcription services"
    )
    GROQ_API_ENDPOINT: str = Field(
        default="https://api.groq.com/openai/v1", description="Groq API endpoint"
    )
    GROQ_MODEL: str = Field(
        default="whisper-large-v3", description="Groq model for transcription"
    )
    GROQ_RATE_LIMIT_RPM: int = Field(
        default=30, description="Groq rate limit requests per minute"
    )
    GROQ_RATE_LIMIT_AUDIO_SECONDS_PER_HOUR: int = Field(
        default=7200, description="Groq audio seconds limit per hour"
    )

    # Audio Processing Configuration
    MAX_AUDIO_FILE_SIZE_MB: int = Field(
        default=25, description="Maximum audio file size in MB"
    )
    COMPRESS_LARGE_FILES: bool = Field(
        default=True, description="Whether to compress large audio files"
    )
    AUDIO_CHUNK_DURATION_SECONDS: int = Field(
        default=600, description="Duration for audio chunks in seconds"
    )

    # Transcription Configuration
    TRANSCRIPTION_PROVIDER: str = Field(
        default="groq", description="Primary transcription provider"
    )
    TRANSCRIPTION_RATE_LIMIT_REQUESTS: int = Field(
        default=30, description="Transcription rate limit requests"
    )
    TRANSCRIPTION_RATE_LIMIT_WINDOW: int = Field(
        default=3600, description="Transcription rate limit window in seconds"
    )

    # Tier Limits Configuration
    FREE_TIER_PROJECTS_PER_MONTH: int = Field(
        default=5, description="Free tier project limit per month"
    )
    FREE_TIER_MAX_DURATION_MINUTES: int = Field(
        default=20, description="Free tier max audio duration in minutes"
    )
    PRO_TIER_MAX_DURATION_MINUTES: int = Field(
        default=60, description="Pro tier max audio duration in minutes"
    )
    BUSINESS_TIER_MAX_DURATION_MINUTES: int = Field(
        default=180, description="Business tier max audio duration in minutes"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

