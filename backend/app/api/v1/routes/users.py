from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.security import get_current_user, UserPrincipal
from app.api.deps import get_supabase

router = APIRouter(prefix="/users", tags=["users"])


class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    tone_of_voice: Optional[str] = None


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[dict[str, Any]] = None
    tone_of_voice: Optional[str] = None


@router.get("/me", response_model=UserProfile)
async def get_me(user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    """Fetch the logged-in user's profile/settings from DB if configured; otherwise return defaults."""
    if supabase:
        try:
            res = supabase.table("profiles").select("*").eq("user_id", user.user_id).execute()
            data = res.data if hasattr(res, "data") else res.get("data")
            if data:
                row = data[0]
                return UserProfile(**{
                    "user_id": user.user_id,
                    "name": row.get("name"),
                    "preferences": row.get("preferences") or {},
                    "tone_of_voice": row.get("tone_of_voice"),
                })
            # Create default profile if not exists
            payload = {"user_id": user.user_id, "name": user.name, "preferences": {}, "tone_of_voice": None}
            res2 = supabase.table("profiles").insert(payload).execute()
            return UserProfile(**payload)
        except Exception:
            # fall back to defaults on error
            pass
    return UserProfile(user_id=user.user_id, name=user.name, preferences={}, tone_of_voice=None)


@router.patch("/me", response_model=UserProfile)
async def update_me(update: UserProfileUpdate, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    """Update profile (name, preferences, tone of voice). Upsert if using Supabase; otherwise echo merge."""
    merged = {"user_id": user.user_id}
    if update.name is not None:
        merged["name"] = update.name
    if update.preferences is not None:
        merged["preferences"] = update.preferences
    if update.tone_of_voice is not None:
        merged["tone_of_voice"] = update.tone_of_voice

    if supabase:
        try:
            payload = {"user_id": user.user_id, **{k: v for k, v in merged.items() if k != "user_id"}}
            res = supabase.table("profiles").upsert(payload).execute()
            # Read back latest
            res2 = supabase.table("profiles").select("*").eq("user_id", user.user_id).execute()
            data = res2.data if hasattr(res2, "data") else res2.get("data")
            row = (data or [{}])[0]
            return UserProfile(**{
                "user_id": user.user_id,
                "name": row.get("name"),
                "preferences": row.get("preferences") or {},
                "tone_of_voice": row.get("tone_of_voice"),
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update profile: {e}")

    # Without DB, just echo merged with basic defaults
    return UserProfile(
        user_id=user.user_id,
        name=merged.get("name", user.name),
        preferences=merged.get("preferences", {}),
        tone_of_voice=merged.get("tone_of_voice"),
    )

