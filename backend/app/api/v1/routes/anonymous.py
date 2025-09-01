"""
Anonymous Upload API Endpoints
Enhanced version with robust error handling for transient issues
"""

import uuid
import asyncio
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.security import get_current_user, UserPrincipal
from app.core.config import settings
from app.api.deps import get_supabase_client
from app.models.anonymous import (
    AnonymousUploadResponse,
    AnonymousStatusResponse,
    AnonymousResultResponse,
    ClaimSessionResponse,
    ClaimSessionRequest,
    AnonymousRateLimitInfo,
    AnonymousErrorResponse
)
from app.services.anonymous_service import AnonymousService

# Create router with prefix
router = APIRouter(prefix="/anonymous", tags=["anonymous"])


async def get_anonymous_service_with_retry(max_retries: int = 3) -> AnonymousService:
    """
    Get AnonymousService with retry logic for initialization issues.
    
    Args:
        max_retries: Maximum number of retry attempts
        
    Returns:
        AnonymousService instance
        
    Raises:
        HTTPException: If service cannot be initialized after retries
    """
    for attempt in range(max_retries):
        try:
            supabase = get_supabase_client()
            if supabase is None:
                raise Exception("Supabase client is None")
            
            service = AnonymousService(supabase)
            return service
            
        except Exception as e:
            logger.warning(f"AnonymousService init attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Failed to initialize AnonymousService after {max_retries} attempts")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "service_unavailable",
                        "message": "Anonymous service temporarily unavailable. Please try again.",
                        "retry_after": 5
                    }
                )


async def execute_with_retry(operation, *args, max_retries: int = 2, **kwargs):
    """
    Execute an operation with retry logic for transient errors.
    
    Args:
        operation: Async function to execute
        *args: Arguments for the operation
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of the operation
        
    Raises:
        HTTPException: If operation fails after all retries
    """
    for attempt in range(max_retries + 1):
        try:
            return await operation(*args, **kwargs)
            
        except HTTPException as e:
            # Don't retry client errors (4xx)
            if 400 <= e.status_code < 500:
                raise
            
            # Retry server errors (5xx) and other exceptions
            if attempt < max_retries:
                logger.warning(f"Operation retry {attempt + 1}: {e}")
                await asyncio.sleep(0.1 * (attempt + 1))
            else:
                raise
                
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Unexpected error retry {attempt + 1}: {e}")
                await asyncio.sleep(0.1 * (attempt + 1))
            else:
                logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "operation_failed",
                        "message": "Operation failed after retries. Please try again.",
                        "correlation_id": str(uuid.uuid4())
                    }
                )


# Health check endpoint
@router.get("/health")
async def anonymous_service_health():
    """Health check for anonymous upload service with enhanced error handling."""
    try:
        service = await get_anonymous_service_with_retry(max_retries=2)
        
        return {
            "status": "healthy",
            "service": "anonymous_upload",
            "limits": {
                "max_file_size_mb": service.usage_limits.max_file_size_mb,
                "max_uploads_per_hour": service.usage_limits.max_uploads_per_hour,
                "max_uploads_per_day": service.usage_limits.max_uploads_per_day,
                "max_duration_minutes": service.usage_limits.max_duration_minutes,
                "allowed_file_types": service.usage_limits.allowed_file_types
            },
            "session_expiry_days": 7
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Anonymous service health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "anonymous_upload",
                "error": "Service dependencies unavailable"
            }
        )


# Rate limit info endpoint
@router.get("/rate-limit", response_model=AnonymousRateLimitInfo)
async def get_rate_limit_info(request: Request):
    """Check rate limit status with enhanced error handling."""
    correlation_id = str(uuid.uuid4())
    
    try:
        # Extract client IP
        client_ip = "unknown"
        if request:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            elif hasattr(request, "client") and request.client:
                client_ip = request.client.host
        
        logger.info("Rate limit check request", correlation_id=correlation_id, client_ip=client_ip)
        
        # Get service and execute with retry
        service = await get_anonymous_service_with_retry()
        response = await execute_with_retry(service.get_rate_limit_info, client_ip)
        
        logger.info("Rate limit info retrieved", correlation_id=correlation_id)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Rate limit check failed", correlation_id=correlation_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "rate_limit_check_failed",
                "message": "Failed to check rate limits. Please try again.",
                "correlation_id": correlation_id
            }
        )


@router.post("/upload", response_model=AnonymousUploadResponse)
async def upload_file_anonymously(
    file: UploadFile = File(..., description="Audio/video file to upload"),
    name: str = Form(..., description="Project name", min_length=1, max_length=100),
    description: Optional[str] = Form(None, description="Optional project description", max_length=500),
    language: Optional[str] = Form("en", description="Language code (ISO 639-1)", max_length=5),
    request: Request = None
):
    """Upload file anonymously with enhanced error handling."""
    correlation_id = str(uuid.uuid4())
    
    try:
        # Extract client info
        client_ip = "unknown"
        user_agent = None
        if request:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            elif hasattr(request, "client") and request.client:
                client_ip = request.client.host
            user_agent = request.headers.get("User-Agent")
        
        logger.info("Anonymous upload request", correlation_id=correlation_id, file_name=file.filename)
        
        # Read file content from UploadFile
        file_content = await file.read()
        
        # Get service - NO RETRY for upload since UploadFile can't be reused
        service = await get_anonymous_service_with_retry()
        response = await service.create_anonymous_upload(
            file_content=file_content,
            file_name=file.filename,
            project_name=name,
            description=description,
            language=language,
            request=request
        )
        
        logger.info("Anonymous upload successful", correlation_id=correlation_id, session_token=response.session_token[:16] + "...")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Anonymous upload failed", 
            correlation_id=correlation_id, 
            error=str(e), 
            error_type=type(e).__name__,
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "upload_failed",
                "message": "Upload failed. Please try again.",
                "correlation_id": correlation_id
            }
        )


@router.get("/{session_token}/status", response_model=AnonymousStatusResponse)
async def get_session_status(session_token: str):
    """Get session status with enhanced error handling."""
    correlation_id = str(uuid.uuid4())
    logger.info("Status check request", correlation_id=correlation_id, session_token=session_token[:16] + "...")
    
    try:
        # Get service and execute with retry - THIS IS WHERE THE 500 ERRORS WERE HAPPENING
        service = await get_anonymous_service_with_retry()
        response = await execute_with_retry(
            service.get_session_status,
            session_token,
            max_retries=2
        )
        
        logger.info("Status check successful", correlation_id=correlation_id, status=response.status)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Status check failed", correlation_id=correlation_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "status_check_failed",
                "message": "Failed to check status. Please try again.",
                "correlation_id": correlation_id
            }
        )


@router.get("/{session_token}", response_model=AnonymousResultResponse)
async def get_transcription_results(session_token: str):
    """Get blurred results with enhanced error handling."""
    correlation_id = str(uuid.uuid4())
    logger.info("Results request", correlation_id=correlation_id, session_token=session_token[:16] + "...")
    
    try:
        # Get service and execute with retry - THIS IS WHERE THE OTHER 500 ERRORS WERE HAPPENING
        service = await get_anonymous_service_with_retry()
        response = await execute_with_retry(
            service.get_blurred_results,
            session_token,
            max_retries=2
        )
        
        logger.info("Results retrieved successfully", correlation_id=correlation_id, is_blurred=response.is_blurred)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Results retrieval failed", correlation_id=correlation_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "results_fetch_failed",
                "message": "Failed to fetch results. Please try again.",
                "correlation_id": correlation_id,
                "signup_suggestion": "Sign up for priority support and guaranteed access!"
            }
        )


@router.post("/{session_token}/claim", response_model=ClaimSessionResponse)
async def claim_anonymous_session(
    session_token: str,
    request_data: ClaimSessionRequest = ClaimSessionRequest(),
    current_user: UserPrincipal = Depends(get_current_user)
):
    """Claim session with enhanced error handling."""
    correlation_id = str(uuid.uuid4())
    user_id = current_user.user_id
    
    logger.info("Claim session request", correlation_id=correlation_id, session_token=session_token[:16] + "...", user_id=user_id)
    
    try:
        # Get service and execute with retry
        service = await get_anonymous_service_with_retry()
        response = await execute_with_retry(
            service.claim_session_for_user,
            session_token, user_id,
            max_retries=1  # Lower retries for claim to avoid duplicate claims
        )
        
        logger.info("Session claimed successfully", correlation_id=correlation_id, user_id=user_id)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Session claim failed", correlation_id=correlation_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "claim_failed",
                "message": "Failed to claim session. Please try again.",
                "correlation_id": correlation_id
            }
        )
