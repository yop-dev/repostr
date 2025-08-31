from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.security import get_current_user, UserPrincipal
from app.api.deps import get_supabase

router = APIRouter(prefix="/projects", tags=["generate"])


class GenerateRequest(BaseModel):
    topic: Optional[str] = None
    prompt_overrides: Optional[str] = None
    tone_of_voice: Optional[str] = None
    extras: dict = Field(default_factory=dict)


@router.post("/{project_id}/generate/blog", status_code=202)
async def generate_blog(project_id: str, body: GenerateRequest, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    output_id = str(uuid4())
    if supabase:
        try:
            supabase.table("outputs").insert({
                "id": output_id,
                "user_id": user.user_id,
                "project_id": project_id,
                "kind": "blog",
                "status": "queued",
                "request": body.model_dump(),
            }).execute()
        except Exception:
            pass
    return {"job_id": output_id, "status": "queued"}


@router.post("/{project_id}/generate/social", status_code=202)
async def generate_social(project_id: str, body: GenerateRequest, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    output_id = str(uuid4())
    if supabase:
        try:
            supabase.table("outputs").insert({
                "id": output_id,
                "user_id": user.user_id,
                "project_id": project_id,
                "kind": "social",
                "status": "queued",
                "request": body.model_dump(),
            }).execute()
        except Exception:
            pass
    return {"job_id": output_id, "status": "queued"}


@router.post("/{project_id}/generate/email", status_code=202)
async def generate_email(project_id: str, body: GenerateRequest, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    output_id = str(uuid4())
    if supabase:
        try:
            supabase.table("outputs").insert({
                "id": output_id,
                "user_id": user.user_id,
                "project_id": project_id,
                "kind": "email",
                "status": "queued",
                "request": body.model_dump(),
            }).execute()
        except Exception:
            pass
    return {"job_id": output_id, "status": "queued"}

