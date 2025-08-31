from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from fastapi.responses import JSONResponse
from app.core.security import get_current_user, UserPrincipal
from app.core.config import settings
from app.api.deps import get_supabase

router = APIRouter(prefix="/projects", tags=["files"])  # shares /projects prefix


@router.post("/{project_id}/upload")
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    user: UserPrincipal = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Upload an audio/video/text file to Supabase Storage under the uploads bucket.
    Stores under {user_id}/{project_id}/{uuid-filename}.
    """
    if not supabase or not settings.SUPABASE_URL:
        raise HTTPException(status_code=503, detail="Storage not configured")

    content = await file.read()
    ext = (file.filename or "").split(".")[-1].lower() if file.filename else "bin"
    object_name = f"{user.user_id}/{project_id}/{uuid4()}.{ext}"

    try:
        bucket = settings.SUPABASE_BUCKET_UPLOADS
        storage = supabase.storage.from_(bucket)
        storage.upload(object_name, content, {
            "contentType": file.content_type or "application/octet-stream",
            "upsert": False,
        })
        public_url = storage.get_public_url(object_name)

        # Optional: record in DB
        try:
            supabase.table("files").insert({
                "id": str(uuid4()),
                "user_id": user.user_id,
                "project_id": project_id,
                "path": object_name,
                "mime_type": file.content_type,
                "size_bytes": len(content),
                "public_url": public_url.get("data", {}).get("publicUrl") if isinstance(public_url, dict) else public_url,
            }).execute()
        except Exception:
            pass

        return {
            "path": object_name,
            "bucket": bucket,
            "public_url": public_url.get("data", {}).get("publicUrl") if isinstance(public_url, dict) else public_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.get("/{project_id}/files")
async def list_files(project_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        return []
    try:
        # Prefer DB if available
        try:
            res = supabase.table("files").select("*").eq("user_id", user.user_id).eq("project_id", project_id).execute()
            data = res.data if hasattr(res, "data") else res.get("data") or []
            if data:
                return data
        except Exception:
            pass
        # Fallback to storage listing
        storage = supabase.storage.from_(settings.SUPABASE_BUCKET_UPLOADS)
        listing = storage.list(path=f"{user.user_id}/{project_id}")
        return listing if listing else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {e}")


@router.delete("/{project_id}/files/{file_id}", status_code=204)
async def delete_file(project_id: str, file_id: str, user: UserPrincipal = Depends(get_current_user), supabase=Depends(get_supabase)):
    if not supabase:
        return
    try:
        # file_id is expected to be a record id in DB; try DB first
        path_value: Optional[str] = None
        try:
            res = supabase.table("files").select("path").eq("id", file_id).eq("user_id", user.user_id).eq("project_id", project_id).execute()
            data = res.data if hasattr(res, "data") else res.get("data") or []
            if data:
                path_value = data[0].get("path")
        except Exception:
            pass

        if not path_value:
            # If not found, assume file_id is the path itself
            path_value = file_id

        supabase.storage.from_(settings.SUPABASE_BUCKET_UPLOADS).remove([path_value])
        try:
            supabase.table("files").delete().eq("id", file_id).eq("user_id", user.user_id).eq("project_id", project_id).execute()
        except Exception:
            pass
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")

