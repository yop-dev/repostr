from datetime import datetime
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from app.core.security import get_current_user, UserPrincipal
from app.api.deps import get_supabase

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Project(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=Project)
async def create_project(payload: ProjectCreate, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    now = datetime.utcnow()
    project = {
        "id": str(uuid4()),
        "user_id": user.user_id,
        "title": payload.title,
        "description": payload.description,
        "created_at": now,
        "updated_at": now,
    }
    if supabase:
        try:
            res = supabase.table("projects").insert(project).execute()
            data = res.data if hasattr(res, "data") else res.get("data")
            if data:
                project = data[0]
        except Exception as e:
            # fall back to returning the generated object
            pass
    return Project(**project)


@router.get("/", response_model=list[Project])
async def list_projects(user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if supabase:
        try:
            res = supabase.table("projects").select("*").eq("user_id", user.user_id).order("created_at", desc=True).execute()
            data = res.data if hasattr(res, "data") else res.get("data") or []
            # Pydantic will coerce datetime strings
            return [Project(**row) for row in data]
        except Exception:
            pass
    return []


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str = Path(...), user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if supabase:
        try:
            res = supabase.table("projects").select("*").eq("id", project_id).eq("user_id", user.user_id).execute()
            data = res.data if hasattr(res, "data") else res.get("data") or []
            if data:
                return Project(**data[0])
        except Exception:
            pass
    raise HTTPException(status_code=404, detail="Project not found")


@router.patch("/{project_id}", response_model=Project)
async def update_project(payload: ProjectUpdate, project_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    update = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    update["updated_at"] = datetime.utcnow()
    if supabase:
        try:
            res = supabase.table("projects").update(update).eq("id", project_id).eq("user_id", user.user_id).execute()
            data = res.data if hasattr(res, "data") else res.get("data") or []
            if data:
                return Project(**data[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update: {e}")
    raise HTTPException(status_code=404, detail="Project not found (no DB)")


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if supabase:
        try:
            supabase.table("projects").delete().eq("id", project_id).eq("user_id", user.user_id).execute()
            return
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")
    # Without DB, pretend success
    return

