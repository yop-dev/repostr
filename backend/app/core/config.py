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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

