"""
Simple Anonymous Upload API Endpoints (without transcription dependencies)
For testing API structure while resolving Python 3.13 compatibility issues
"""

import uuid
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel

# Simple response models without transcription dependencies
class SimpleAnonymousUploadResponse(BaseModel):
    session_token: str
    project_id: str
    file_name: str
    file_size: int
    status: str
    estimated_time_seconds: int
    expires_at: datetime
    message: str

class SimpleAnonymousStatusResponse(BaseModel):
    session_token: str
    status: str
    file_name: str
    file_size: int
    created_at: datetime
    expires_at: datetime
    is_expired: bool
    message: str

class SimpleAnonymousResultResponse(BaseModel):
    session_token: str
    status: str
    is_blurred: bool
    signup_required: bool
    expires_at: datetime
    conversion_message: str
    demo_preview: str

# Create router
router = APIRouter(prefix="/anonymous", tags=["anonymous"])

# In-memory storage for demo (replace with database in production)
demo_sessions = {}

@router.post("/upload", response_model=SimpleAnonymousUploadResponse)
async def upload_file_anonymously(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    request: Request = None
):
    """
    Demo anonymous upload endpoint (without transcription processing).
    """
    try:
        # Validate file
        if not file or not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "no_file_provided",
                    "message": "No file was uploaded.",
                    "signup_suggestion": "Sign up to access our full file upload interface!"
                }
            )
        
        # Read file content for size validation
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size (10MB limit for anonymous)
        max_size = 10 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "file_too_large",
                    "message": f"File size exceeds 10MB limit for anonymous uploads.",
                    "details": {
                        "file_size_mb": round(file_size / (1024 * 1024), 2),
                        "max_size_mb": 10
                    },
                    "signup_suggestion": "Sign up for free to upload files up to 25MB!"
                }
            )
        
        # Generate session token and project ID
        session_token = f"demo_session_{uuid.uuid4().hex}"
        project_id = str(uuid.uuid4())
        
        # Store session info (demo)
        expires_at = datetime.utcnow() + timedelta(days=7)
        demo_sessions[session_token] = {
            "project_id": project_id,
            "file_name": file.filename,
            "file_size": file_size,
            "name": name,
            "description": description,
            "language": language,
            "status": "processing",
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "demo_content": f"This is a demo transcription for the file '{file.filename}'. In the real implementation, this would contain the actual transcribed content from your audio file. The transcription would be processed using advanced AI models to convert speech to text with high accuracy."
        }
        
        return SimpleAnonymousUploadResponse(
            session_token=session_token,
            project_id=project_id,
            file_name=file.filename,
            file_size=file_size,
            status="processing",
            estimated_time_seconds=30,
            expires_at=expires_at,
            message="Demo upload successful. In production, this would start real transcription processing."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "upload_failed",
                "message": f"Demo upload failed: {str(e)}",
                "signup_suggestion": "Sign up for priority support and more reliable processing!"
            }
        )

@router.get("/{session_token}/status", response_model=SimpleAnonymousStatusResponse)
async def get_session_status(session_token: str):
    """Demo status check endpoint."""
    
    if session_token not in demo_sessions:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "session_not_found",
                "message": "Session token not found or invalid.",
                "signup_suggestion": "Sign up to create an account and manage your transcriptions!"
            }
        )
    
    session = demo_sessions[session_token]
    
    # Simulate processing completion after 30 seconds
    elapsed = (datetime.utcnow() - session["created_at"]).total_seconds()
    if elapsed > 30:
        session["status"] = "completed"
    
    return SimpleAnonymousStatusResponse(
        session_token=session_token,
        status=session["status"],
        file_name=session["file_name"],
        file_size=session["file_size"],
        created_at=session["created_at"],
        expires_at=session["expires_at"],
        is_expired=datetime.utcnow() > session["expires_at"],
        message=f"Demo status: {session['status']}. Real implementation would show actual processing progress."
    )

@router.get("/{session_token}", response_model=SimpleAnonymousResultResponse)
async def get_transcription_results(session_token: str):
    """Demo blurred results endpoint."""
    
    if session_token not in demo_sessions:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "session_not_found",
                "message": "Session token not found or invalid.",
                "signup_suggestion": "Sign up to create an account and manage your transcriptions!"
            }
        )
    
    session = demo_sessions[session_token]
    
    if session["status"] != "completed":
        raise HTTPException(
            status_code=202,
            detail={
                "error": "still_processing",
                "message": "Transcription is still being processed. Please check status endpoint.",
                "session_token": session_token
            }
        )
    
    # Create blurred preview
    full_content = session["demo_content"]
    preview = full_content[:150] + "..."
    
    return SimpleAnonymousResultResponse(
        session_token=session_token,
        status="completed",
        is_blurred=True,
        signup_required=True,
        expires_at=session["expires_at"],
        conversion_message=f"Your demo transcription is ready! Sign up free to view the complete content and unlock powerful repurposing features!",
        demo_preview=preview
    )

@router.get("/health")
async def anonymous_service_health():
    """Demo health check."""
    return {
        "status": "healthy",
        "service": "anonymous_upload_demo",
        "message": "Demo version - transcription dependencies disabled due to Python 3.13 compatibility",
        "python_version": "3.13",
        "note": "This is a simplified version for testing API structure"
    }

@router.get("/rate-limit")
async def get_rate_limit_info():
    """Demo rate limit info."""
    return {
        "uploads_used_hour": 1,
        "uploads_used_day": 2,
        "uploads_remaining_hour": 2,
        "uploads_remaining_day": 3,
        "reset_time_hour": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "reset_time_day": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_limited": False,
        "demo_mode": True
    }