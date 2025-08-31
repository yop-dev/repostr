from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_current_user, UserPrincipal
from app.api.deps import get_supabase

router = APIRouter(tags=["templates"])  # root-level endpoints


class Template(BaseModel):
    id: str
    name: str
    type: str  # e.g., blog | linkedin | twitter | instagram | email
    prompt: str
    is_custom: bool = False


class TemplateCreate(BaseModel):
    name: str
    type: str
    prompt: str


DEFAULT_TEMPLATES = [
    {"id": "blog_basic", "name": "Blog: Basic", "type": "blog", "prompt": "Write a structured blog post.", "is_custom": False},
    {"id": "linkedin_insight", "name": "LinkedIn: Insight", "type": "linkedin", "prompt": "Write a professional LinkedIn post with a hook and insights.", "is_custom": False},
    {"id": "twitter_thread", "name": "Twitter/X Thread", "type": "twitter", "prompt": "Create a compelling X thread with 5-8 tweets.", "is_custom": False},
]


@router.get("/templates")
async def list_templates(user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    custom = []
    if supabase:
        try:
            res = supabase.table("templates").select("*").eq("user_id", user.user_id).execute()
            custom = res.data if hasattr(res, "data") else res.get("data") or []
        except Exception:
            pass
    return DEFAULT_TEMPLATES + custom


@router.post("/templates/custom")
async def create_custom_template(payload: TemplateCreate, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        raise HTTPException(status_code=503, detail="Templates storage not configured")
    try:
        from uuid import uuid4

        new_id = str(uuid4())
        res = supabase.table("templates").insert({
            "id": new_id,
            "user_id": user.user_id,
            "name": payload.name,
            "type": payload.type,
            "prompt": payload.prompt,
            "is_custom": True,
        }).execute()
        data = res.data if hasattr(res, "data") else res.get("data") or []
        return data[0] if data else {"id": new_id, **payload.model_dump(), "is_custom": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {e}")


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(template_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        return
    try:
        supabase.table("templates").delete().eq("id", template_id).eq("user_id", user.user_id).execute()
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {e}")

