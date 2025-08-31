from typing import Optional
from fastapi import Depends
from app.core.config import settings


def get_supabase_client():
    """Create and return a Supabase client if env is configured, else None.
    Import inside the function to avoid hard dependency during boot.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return None
    try:
        from supabase import create_client

        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    except Exception:
        return None


SupabaseClient = Optional[object]


def get_supabase() -> SupabaseClient:
    return get_supabase_client()

