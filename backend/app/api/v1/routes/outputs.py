from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.security import get_current_user, UserPrincipal
from app.api.deps import get_supabase

router = APIRouter(prefix="/projects", tags=["outputs"])


class Output(BaseModel):
    id: str
    project_id: str
    kind: str
    status: str
    body: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class OutputUpdate(BaseModel):
    body: Optional[str] = None
    metadata: Optional[dict] = None


@router.get("/{project_id}/outputs")
async def list_outputs(project_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        return []
    try:
        res = supabase.table("outputs").select("*").eq("project_id", project_id).eq("user_id", user.user_id).execute()
        data = res.data if hasattr(res, "data") else res.get("data") or []
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list outputs: {e}")


@router.get("/{project_id}/outputs/{output_id}")
async def get_output(project_id: str, output_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        raise HTTPException(status_code=404, detail="Output not found")
    try:
        res = supabase.table("outputs").select("*").eq("id", output_id).eq("project_id", project_id).eq("user_id", user.user_id).execute()
        data = res.data if hasattr(res, "data") else res.get("data") or []
        if not data:
            raise HTTPException(status_code=404, detail="Output not found")
        return data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch output: {e}")


@router.patch("/{project_id}/outputs/{output_id}")
async def update_output(project_id: str, output_id: str, update: OutputUpdate, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        raise HTTPException(status_code=404, detail="Output not found")
    try:
        payload = {k: v for k, v in update.model_dump(exclude_none=True).items()}
        res = supabase.table("outputs").update(payload).eq("id", output_id).eq("project_id", project_id).eq("user_id", user.user_id).execute()
        data = res.data if hasattr(res, "data") else res.get("data") or []
        if not data:
            raise HTTPException(status_code=404, detail="Output not found")
        return data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update output: {e}")


@router.delete("/{project_id}/outputs/{output_id}", status_code=204)
async def delete_output(project_id: str, output_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        return
    try:
        supabase.table("outputs").delete().eq("id", output_id).eq("project_id", project_id).eq("user_id", user.user_id).execute()
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete output: {e}")

