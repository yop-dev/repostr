"""
Project API Endpoints
Handles project creation, file upload, and transcription
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.security import get_current_user, UserPrincipal
from app.core.config import settings
from app.api.deps import get_supabase_client
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectListResponse,
    FileUploadResponse,
    TranscriptionJobResponse,
    ProjectWithTranscription,
    UserUsageStats,
    ProjectStatus,
    TranscriptionStatus
)
from app.services.background_tasks import background_service
from app.services.transcription.audio_utils import AudioProcessor

router = APIRouter(prefix="/transcription", tags=["transcription"])


def check_user_limits(user_id: str, supabase) -> UserUsageStats:
    """
    Check user's usage against tier limits.
    
    Args:
        user_id: User ID
        supabase: Supabase client
        
    Returns:
        User usage stats
        
    Raises:
        HTTPException: If limits exceeded
    """
    # Get current month's start date
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    # Count projects this month
    projects_response = supabase.table("projects").select("id, duration_seconds").eq(
        "user_id", user_id
    ).gte("created_at", month_start.isoformat()).execute()
    
    projects_this_month = len(projects_response.data)
    
    # Calculate total duration
    total_duration_seconds = sum(
        p.get("duration_seconds", 0) or 0 for p in projects_response.data
    )
    total_duration_minutes = total_duration_seconds / 60
    
    # Get all-time project count
    all_projects_response = supabase.table("projects").select("id").eq(
        "user_id", user_id
    ).execute()
    total_projects = len(all_projects_response.data)
    
    stats = UserUsageStats(
        projects_this_month=projects_this_month,
        monthly_limit=settings.FREE_TIER_MAX_PROJECTS_PER_MONTH,
        total_projects=total_projects,
        total_duration_minutes=total_duration_minutes,
        tier="free"
    )
    
    # Check if limit exceeded
    if projects_this_month >= settings.FREE_TIER_MAX_PROJECTS_PER_MONTH:
        raise HTTPException(
            status_code=403,
            detail=f"Monthly project limit reached ({settings.FREE_TIER_MAX_PROJECTS_PER_MONTH} projects). Upgrade to continue."
        )
    
    return stats


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Upload an audio/video file and create a new project.
    
    Args:
        file: Audio/video file to upload
        name: Project name
        description: Optional project description
        language: Optional language code (ISO 639-1)
        tags: Optional comma-separated tags
        current_user: Current authenticated user
        
    Returns:
        File upload response with project ID
    """
    user_id = current_user.user_id
    supabase = get_supabase_client()
    
    try:
        # Check user limits
        usage_stats = check_user_limits(user_id, supabase)
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_extensions = settings.ALLOWED_AUDIO_EXTENSIONS.split(",")
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Generate unique file path
        project_id = str(uuid.uuid4())
        storage_path = f"{user_id}/{project_id}/{file.filename}"
        
        # Upload to Supabase Storage
        logger.info(f"Uploading file to Supabase: {storage_path}")
        upload_response = supabase.storage.from_(settings.SUPABASE_BUCKET_UPLOADS).upload(
            storage_path,
            file_content,
            {"content-type": file.content_type}
        )
        
        # Get public URL (optional, if bucket is public)
        file_url = supabase.storage.from_(settings.SUPABASE_BUCKET_UPLOADS).get_public_url(storage_path)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Create project in database
        project_data = {
            "id": project_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "language": language,
            "tags": tag_list,
            "status": ProjectStatus.PENDING.value,
            "file_name": file.filename,
            "file_size": file_size,
            "file_url": file_url,
            "storage_path": storage_path,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        project_response = supabase.table("projects").insert(project_data).execute()
        
        logger.info(f"Created project {project_id} for user {user_id}")
        
        return FileUploadResponse(
            project_id=project_id,
            file_name=file.filename,
            file_size=file_size,
            storage_path=storage_path,
            upload_url=file_url,
            message="File uploaded successfully. Use /transcribe endpoint to start transcription."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/{project_id}/transcribe", response_model=TranscriptionJobResponse)
async def start_transcription(
    project_id: str,
    language: Optional[str] = None,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Start transcription for a project.
    
    Args:
        project_id: Project ID
        language: Optional language code override
        current_user: Current authenticated user
        
    Returns:
        Transcription job response
    """
    user_id = current_user["sub"]
    supabase = get_supabase_client()
    
    try:
        # Get project
        project_response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).eq("user_id", user_id).execute()
        
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_response.data[0]
        
        # Check if already transcribed or processing
        if project.get("transcription_status") == TranscriptionStatus.PROCESSING.value:
            raise HTTPException(status_code=400, detail="Transcription already in progress")
        
        if project.get("transcription_status") == TranscriptionStatus.COMPLETED.value:
            raise HTTPException(status_code=400, detail="Project already transcribed")
        
        # Check audio duration limit for free tier
        if project.get("duration_seconds"):
            duration_minutes = project["duration_seconds"] / 60
            if duration_minutes > settings.FREE_TIER_MAX_DURATION_MINUTES:
                raise HTTPException(
                    status_code=403,
                    detail=f"Audio duration exceeds free tier limit ({settings.FREE_TIER_MAX_DURATION_MINUTES} minutes)"
                )
        
        # Use project language if not overridden
        if not language:
            language = project.get("language")
        
        # Submit transcription task
        task_id = background_service.submit_transcription_task(
            project_id=project_id,
            storage_path=project["storage_path"],
            user_id=user_id,
            language=language
        )
        
        # Estimate processing time (rough estimate)
        audio_processor = AudioProcessor()
        estimated_time = 30  # Default estimate
        
        # Update project status
        supabase.table("projects").update({
            "transcription_status": TranscriptionStatus.PENDING.value,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", project_id).execute()
        
        return TranscriptionJobResponse(
            project_id=project_id,
            status=TranscriptionStatus.PENDING,
            message="Transcription started. Check status with GET /projects/{project_id}",
            estimated_time_seconds=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start transcription: {str(e)}")


@router.get("/{project_id}", response_model=ProjectWithTranscription)
async def get_project(
    project_id: str,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Get project details with transcription.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        
    Returns:
        Project with transcription data
    """
    user_id = current_user["sub"]
    supabase = get_supabase_client()
    
    try:
        # Get project
        project_response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).eq("user_id", user_id).execute()
        
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project_response.data[0]
        project = Project(**project_data)
        
        # Get transcription if available
        transcription = None
        if project.transcription_id:
            trans_response = supabase.table("transcriptions").select("*").eq(
                "id", project.transcription_id
            ).execute()
            
            if trans_response.data:
                from app.models.project import Transcription
                transcription = Transcription(**trans_response.data[0])
        
        return ProjectWithTranscription(
            project=project,
            transcription=transcription
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[ProjectStatus] = None,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    List user's projects with pagination.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        status: Optional status filter
        current_user: Current authenticated user
        
    Returns:
        Paginated project list
    """
    user_id = current_user["sub"]
    supabase = get_supabase_client()
    
    try:
        # Build query
        query = supabase.table("projects").select("*").eq("user_id", user_id)
        
        if status:
            query = query.eq("status", status.value)
        
        # Get total count
        count_response = query.execute()
        total = len(count_response.data)
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)
        
        # Execute query
        response = query.execute()
        
        # Convert to models
        projects = [Project(**p) for p in response.data]
        
        return ProjectListResponse(
            projects=projects,
            total=total,
            page=page,
            per_page=per_page,
            has_more=(offset + per_page) < total
        )
        
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Update project metadata.
    
    Args:
        project_id: Project ID
        update_data: Fields to update
        current_user: Current authenticated user
        
    Returns:
        Updated project
    """
    user_id = current_user["sub"]
    supabase = get_supabase_client()
    
    try:
        # Check project exists and belongs to user
        project_response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).eq("user_id", user_id).execute()
        
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Build update data
        updates = {
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if update_data.name is not None:
            updates["name"] = update_data.name
        if update_data.description is not None:
            updates["description"] = update_data.description
        if update_data.tags is not None:
            updates["tags"] = update_data.tags
        
        # Update project
        update_response = supabase.table("projects").update(updates).eq(
            "id", project_id
        ).execute()
        
        return Project(**update_response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Delete a project and its associated data.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    user_id = current_user["sub"]
    supabase = get_supabase_client()
    
    try:
        # Check project exists and belongs to user
        project_response = supabase.table("projects").select("*").eq(
            "id", project_id
        ).eq("user_id", user_id).execute()
        
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_response.data[0]
        
        # Delete file from storage
        if project.get("storage_path"):
            try:
                supabase.storage.from_(settings.SUPABASE_BUCKET_UPLOADS).remove(
                    [project["storage_path"]]
                )
            except Exception as e:
                logger.warning(f"Failed to delete file from storage: {str(e)}")
        
        # Delete transcription
        if project.get("transcription_id"):
            supabase.table("transcriptions").delete().eq(
                "id", project["transcription_id"]
            ).execute()
        
        # Delete project
        supabase.table("projects").delete().eq("id", project_id).execute()
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@router.get("/usage/stats", response_model=UserUsageStats)
async def get_usage_stats(
    current_user: UserPrincipal = Depends(get_current_user)
):
    """
    Get user's usage statistics.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User usage statistics
    """
    user_id = current_user["sub"]
    supabase = get_supabase_client()
    
    try:
        return check_user_limits(user_id, supabase)
    except HTTPException as e:
        # Return stats even if limits exceeded
        if e.status_code == 403:
            return check_user_limits.__wrapped__(user_id, supabase)
        raise
