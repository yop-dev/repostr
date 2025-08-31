from fastapi import APIRouter, Depends, HTTPException
from app.core.security import admin_required, UserPrincipal
from app.api.deps import get_supabase

router = APIRouter(prefix="/admin", tags=["admin"])  # optional


@router.get("/users")
async def list_users(_: UserPrincipal = Depends(admin_required), supabase=Depends(get_supabase)):
    if not supabase:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        # If using Clerk, typically you'd sync a shadow user table; otherwise this could be profiles
        res = supabase.table("profiles").select("*").execute()
        return res.data if hasattr(res, "data") else res.get("data") or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {e}")


@router.get("/projects")
async def list_projects(_: UserPrincipal = Depends(admin_required), supabase=Depends(get_supabase)):
    if not supabase:
        raise HTTPException(status_code=501, detail="Supabase not configured")
    try:
        res = supabase.table("projects").select("*").order("created_at", desc=True).execute()
        return res.data if hasattr(res, "data") else res.get("data") or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {e}")
