"""
Anonymous Session Service
Business logic for anonymous upload functionality following backend best practices
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import asyncio

from loguru import logger
from fastapi import HTTPException, Request
from supabase import Client as SupabaseClient

from app.models.anonymous import (
    AnonymousSession,
    AnonymousSessionCreate,
    AnonymousSessionStatus,
    AnonymousUploadResponse,
    AnonymousStatusResponse,
    AnonymousResultResponse,
    ClaimSessionResponse,
    TranscriptionPreview,
    AnonymousUsageLimits,
    AnonymousRateLimitInfo,
    create_conversion_message,
    create_file_info_metadata,
    create_usage_stats_metadata,
    generate_preview_text
)
from app.core.config import settings
from app.services.transcription.manager import TranscriptionManager
from app.services.background_tasks import background_service


class AnonymousService:
    """
    Service layer for anonymous upload functionality.
    Handles session management, file uploads, and user conversion.
    """
    
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
        self.transcription_manager = TranscriptionManager()
        self.usage_limits = AnonymousUsageLimits()
        
    async def create_anonymous_upload(
        self,
        file_content: bytes,
        file_name: str,
        project_name: str,
        description: Optional[str] = None,
        language: Optional[str] = "en",
        request: Optional[Request] = None
    ) -> AnonymousUploadResponse:
        """
        Create anonymous upload session and start processing.
        
        Args:
            file_content: Raw file bytes
            file_name: Original file name
            project_name: User-provided project name
            description: Optional project description
            language: Language code for transcription
            request: FastAPI request object for IP/user-agent
            
        Returns:
            AnonymousUploadResponse with session token and status
            
        Raises:
            HTTPException: If validation fails or rate limits exceeded
        """
        correlation_id = str(uuid.uuid4())
        logger.info(
            "Starting anonymous upload",
            correlation_id=correlation_id,
            file_name=file_name,
            file_size=len(file_content),
            project_name=project_name
        )
        
        try:
            # Extract client info
            client_ip = self._get_client_ip(request)
            user_agent = self._get_user_agent(request)
            
            # Check rate limits
            await self._check_rate_limits(client_ip, correlation_id)
            
            # Validate file
            self._validate_file(file_content, file_name, correlation_id)
            
            # Generate session token
            session_token = self._generate_session_token()
            
            # Create storage path
            storage_path = f"anonymous/{session_token[:16]}/{file_name}"
            
            # Upload file to storage
            await self._upload_file_to_storage(
                file_content, storage_path, correlation_id
            )
            
            # Create anonymous session record
            session_data = AnonymousSessionCreate(
                session_token=session_token,
                file_name=file_name,
                file_size=len(file_content),
                storage_path=storage_path,
                ip_address=client_ip,
                user_agent=user_agent
            )
            
            session = await self._create_session_record(
                session_data, correlation_id
            )
            
            # Create project record
            project_id = await self._create_anonymous_project(
                session.id,
                project_name,
                description,
                language,
                len(file_content),
                correlation_id
            )
            
            # Update session with project_id
            await self._update_session_project(session.id, project_id, correlation_id)
            
            # Start transcription in background
            estimated_time = await self._start_transcription_job(
                project_id,
                storage_path,
                session_token,
                language,
                correlation_id
            )
            
            # Track usage for rate limiting
            await self._track_anonymous_usage(client_ip, correlation_id)
            
            logger.info(
                "Anonymous upload created successfully",
                correlation_id=correlation_id,
                session_token=session_token[:16] + "...",
                project_id=project_id,
                estimated_time=estimated_time
            )
            
            return AnonymousUploadResponse(
                session_token=session_token,
                project_id=project_id,
                file_name=file_name,
                file_size=len(file_content),
                status=AnonymousSessionStatus.PROCESSING,
                estimated_time_seconds=estimated_time,
                expires_at=datetime.utcnow() + timedelta(days=7),
                message=f"File uploaded successfully. Processing will complete in approximately {estimated_time} seconds."
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to create anonymous upload",
                correlation_id=correlation_id,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "upload_failed",
                    "message": "Failed to process upload. Please try again.",
                    "correlation_id": correlation_id
                }
            )
    
    async def get_session_status(
        self,
        session_token: str
    ) -> AnonymousStatusResponse:
        """
        Get current status of anonymous session.
        
        Args:
            session_token: Session token from upload
            
        Returns:
            AnonymousStatusResponse with current status
            
        Raises:
            HTTPException: If session not found or expired
        """
        correlation_id = str(uuid.uuid4())
        logger.info(
            "Getting session status",
            correlation_id=correlation_id,
            session_token=session_token[:16] + "..."
        )
        
        try:
            # Get session from database
            session = await self._get_session_by_token(session_token, correlation_id)
            
            # Check if expired
            if self._is_session_expired(session.expires_at):
                raise HTTPException(
                    status_code=410,
                    detail={
                        "error": "session_expired",
                        "message": "This session has expired. Anonymous sessions are valid for 7 days.",
                        "signup_suggestion": "Sign up to keep your transcriptions forever!"
                    }
                )
            
            # Get progress if processing
            progress_percentage = None
            estimated_time_remaining = None
            error_message = None
            
            if session.status == AnonymousSessionStatus.PROCESSING:
                # Check transcription progress
                progress_info = await self._get_transcription_progress(
                    session.project_id, correlation_id
                )
                progress_percentage = progress_info.get("progress_percentage")
                estimated_time_remaining = progress_info.get("estimated_time_remaining")
            elif session.status == AnonymousSessionStatus.FAILED:
                error_message = await self._get_error_message(
                    session.project_id, correlation_id
                )
            
            return AnonymousStatusResponse(
                session_token=session_token,
                status=session.status,
                progress_percentage=progress_percentage,
                estimated_time_remaining=estimated_time_remaining,
                file_name=session.file_name,
                file_size=session.file_size,
                created_at=session.created_at,
                expires_at=session.expires_at,
                is_expired=False,
                error_message=error_message
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to get session status",
                correlation_id=correlation_id,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "status_check_failed",
                    "message": "Failed to check status. Please try again.",
                    "correlation_id": correlation_id
                }
            )
    
    async def get_blurred_results(
        self,
        session_token: str
    ) -> AnonymousResultResponse:
        """
        Get blurred transcription results for conversion.
        
        Args:
            session_token: Session token from upload
            
        Returns:
            AnonymousResultResponse with blurred content and conversion CTA
            
        Raises:
            HTTPException: If session not found, expired, or not ready
        """
        correlation_id = str(uuid.uuid4())
        logger.info(
            "Getting blurred results",
            correlation_id=correlation_id,
            session_token=session_token[:16] + "..."
        )
        
        try:
            # Get session from database
            session = await self._get_session_by_token(session_token, correlation_id)
            
            # Check if expired
            if self._is_session_expired(session.expires_at):
                raise HTTPException(
                    status_code=410,
                    detail={
                        "error": "session_expired",
                        "message": "This session has expired. Anonymous sessions are valid for 7 days.",
                        "signup_suggestion": "Sign up to keep your transcriptions forever!"
                    }
                )
            
            # Check if still processing
            if session.status == AnonymousSessionStatus.PROCESSING:
                raise HTTPException(
                    status_code=202,
                    detail={
                        "error": "still_processing",
                        "message": "Transcription is still being processed. Please check status endpoint.",
                        "session_token": session_token
                    }
                )
            
            # Check if failed
            if session.status == AnonymousSessionStatus.FAILED:
                error_message = await self._get_error_message(
                    session.project_id, correlation_id
                )
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "processing_failed",
                        "message": f"Processing failed: {error_message}",
                        "signup_suggestion": "Sign up to get priority support and more reliable processing!"
                    }
                )
            
            # Get transcription data
            transcription = await self._get_transcription_by_session(
                session.id, correlation_id
            )
            
            if not transcription:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "transcription_not_found",
                        "message": "Transcription not found for this session.",
                        "signup_suggestion": "Sign up to create an account and manage your transcriptions!"
                    }
                )
            
            # Create blurred preview
            preview_text = generate_preview_text(transcription["text"], 150)
            
            transcription_preview = TranscriptionPreview(
                preview_text=preview_text,
                total_word_count=transcription.get("word_count", 0),
                duration_seconds=transcription.get("duration_seconds", 0),
                language=transcription.get("language", "en"),
                confidence=transcription.get("confidence"),
                processing_time_ms=transcription.get("processing_time_ms")
            )
            
            # Create conversion message
            conversion_message = create_conversion_message(transcription_preview)
            
            # Create file info for display
            file_info = create_file_info_metadata(
                session.file_name,
                session.file_size,
                transcription_preview.duration_seconds
            )
            
            # Create usage stats for social proof
            usage_stats = create_usage_stats_metadata()
            
            logger.info(
                "Blurred results generated",
                correlation_id=correlation_id,
                word_count=transcription_preview.total_word_count,
                preview_length=len(preview_text)
            )
            
            return AnonymousResultResponse(
                session_token=session_token,
                status=session.status,
                transcription_preview=transcription_preview,
                is_blurred=True,
                signup_required=True,
                expires_at=session.expires_at,
                conversion_message=conversion_message,
                file_info=file_info,
                usage_stats=usage_stats
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to get blurred results",
                correlation_id=correlation_id,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "results_fetch_failed",
                    "message": "Failed to fetch results. Please try again.",
                    "correlation_id": correlation_id
                }
            )
    
    async def claim_session_for_user(
        self,
        session_token: str,
        user_id: str
    ) -> ClaimSessionResponse:
        """
        Claim anonymous session for authenticated user.
        
        Args:
            session_token: Session token to claim
            user_id: Authenticated user ID from JWT
            
        Returns:
            ClaimSessionResponse with full content and project data
            
        Raises:
            HTTPException: If session not found, expired, or already claimed
        """
        correlation_id = str(uuid.uuid4())
        logger.info(
            "Claiming session for user",
            correlation_id=correlation_id,
            session_token=session_token[:16] + "...",
            user_id=user_id
        )
        
        try:
            # Use database function for atomic claim operation
            result = await self._claim_session_atomic(
                session_token, user_id, correlation_id
            )
            
            if not result["success"]:
                error_code = result["error"]
                if error_code == "Session not found":
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "success": False,
                            "error": "session_not_found",
                            "message": "Session token not found or invalid."
                        }
                    )
                elif error_code == "Session expired":
                    raise HTTPException(
                        status_code=410,
                        detail={
                            "success": False,
                            "error": "session_expired",
                            "message": "This session has expired and cannot be claimed."
                        }
                    )
                elif error_code == "Session already claimed":
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "success": False,
                            "error": "already_claimed",
                            "message": "This session has already been claimed by another user."
                        }
                    )
                else:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "success": False,
                            "error": "claim_failed",
                            "message": f"Failed to claim session: {error_code}"
                        }
                    )
            
            # Get full project and transcription data
            project_data = await self._get_project_data(
                result["project_id"], correlation_id
            )
            transcription_data = await self._get_transcription_data(
                result["transcription_id"], correlation_id
            )
            
            logger.info(
                "Session claimed successfully",
                correlation_id=correlation_id,
                user_id=user_id,
                project_id=result["project_id"],
                transcription_id=result["transcription_id"]
            )
            
            return ClaimSessionResponse(
                success=True,
                project_id=result["project_id"],
                transcription_id=result["transcription_id"],
                full_content=transcription_data.get("content"),
                claimed_at=datetime.fromisoformat(result["claimed_at"]),
                error=None,
                project_data=project_data,
                transcription_data=transcription_data
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to claim session",
                correlation_id=correlation_id,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": "claim_failed",
                    "message": "Failed to claim session. Please try again.",
                    "correlation_id": correlation_id
                }
            )
    
    async def get_rate_limit_info(
        self,
        client_ip: str
    ) -> AnonymousRateLimitInfo:
        """
        Get current rate limit status for IP address.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            AnonymousRateLimitInfo with current usage and limits
        """
        correlation_id = str(uuid.uuid4())
        
        try:
            # Get current usage from database/cache
            hour_usage = await self._get_hourly_usage(client_ip)
            day_usage = await self._get_daily_usage(client_ip)
            
            # Calculate remaining
            hour_remaining = max(0, self.usage_limits.max_uploads_per_hour - hour_usage)
            day_remaining = max(0, self.usage_limits.max_uploads_per_day - day_usage)
            
            # Calculate reset times
            now = datetime.utcnow()
            hour_reset = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            day_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            # Check if currently limited
            is_limited = hour_remaining <= 0 or day_remaining <= 0
            
            return AnonymousRateLimitInfo(
                uploads_used_hour=hour_usage,
                uploads_used_day=day_usage,
                uploads_remaining_hour=hour_remaining,
                uploads_remaining_day=day_remaining,
                reset_time_hour=hour_reset,
                reset_time_day=day_reset,
                is_limited=is_limited
            )
            
        except Exception as e:
            logger.error(
                "Failed to get rate limit info",
                correlation_id=correlation_id,
                error=str(e)
            )
            # Return conservative defaults on error
            return AnonymousRateLimitInfo(
                uploads_used_hour=self.usage_limits.max_uploads_per_hour,
                uploads_used_day=self.usage_limits.max_uploads_per_day,
                uploads_remaining_hour=0,
                uploads_remaining_day=0,
                reset_time_hour=datetime.utcnow() + timedelta(hours=1),
                reset_time_day=datetime.utcnow() + timedelta(days=1),
                is_limited=True
            )
    
    # Private helper methods
    
    def _is_session_expired(self, session_expires_at: datetime) -> bool:
        """Check if session is expired, handling timezone-aware comparisons."""
        current_time = datetime.utcnow()
        if hasattr(session_expires_at, 'tzinfo') and session_expires_at.tzinfo:
            # Database datetime is timezone-aware, make current_time aware too
            from datetime import timezone
            current_time = current_time.replace(tzinfo=timezone.utc)
        return session_expires_at < current_time
    
    def _get_client_ip(self, request: Optional[Request]) -> Optional[str]:
        """Extract client IP from request headers."""
        if not request:
            return None
        
        # Check common proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
    
    def _get_user_agent(self, request: Optional[Request]) -> Optional[str]:
        """Extract user agent from request headers."""
        if not request:
            return None
        return request.headers.get("User-Agent")
    
    def _generate_session_token(self) -> str:
        """Generate secure session token."""
        return secrets.token_urlsafe(48)  # 64 characters, URL-safe
    
    def _validate_file(
        self,
        file_content: bytes,
        file_name: str,
        correlation_id: str
    ) -> None:
        """
        Validate uploaded file against anonymous limits.
        
        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > self.usage_limits.max_file_size_mb:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "file_too_large",
                    "message": f"File size exceeds {self.usage_limits.max_file_size_mb}MB limit for anonymous uploads.",
                    "details": {
                        "file_size_mb": round(file_size_mb, 2),
                        "max_size_mb": self.usage_limits.max_file_size_mb
                    },
                    "signup_suggestion": "Sign up for free to upload files up to 25MB!"
                }
            )
        
        # Check file extension
        file_ext = Path(file_name).suffix.lower()
        if file_ext not in self.usage_limits.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_file_type",
                    "message": f"File type {file_ext} not supported for anonymous uploads.",
                    "details": {
                        "allowed_types": self.usage_limits.allowed_file_types
                    },
                    "signup_suggestion": "Sign up for free to upload more file types!"
                }
            )
        
        logger.info(
            "File validation passed",
            correlation_id=correlation_id,
            file_size_mb=round(file_size_mb, 2),
            file_ext=file_ext
        )
    
    async def _check_rate_limits(
        self,
        client_ip: Optional[str],
        correlation_id: str
    ) -> None:
        """
        Check if client has exceeded rate limits.
        
        Raises:
            HTTPException: If rate limits exceeded
        """
        if not client_ip:
            logger.warning(
                "No client IP for rate limiting",
                correlation_id=correlation_id
            )
            return
        
        # Get current usage
        hour_usage = await self._get_hourly_usage(client_ip)
        day_usage = await self._get_daily_usage(client_ip)
        
        # Check hourly limit
        if hour_usage >= self.usage_limits.max_uploads_per_hour:
            now = datetime.utcnow()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            retry_after = int((next_hour - now).total_seconds())
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Upload limit reached. Try again in {retry_after // 60} minutes or sign up for unlimited uploads.",
                    "retry_after": retry_after,
                    "signup_suggestion": "Sign up for free to get unlimited uploads and advanced features!"
                }
            )
        
        # Check daily limit
        if day_usage >= self.usage_limits.max_uploads_per_day:
            now = datetime.utcnow()
            next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            retry_after = int((next_day - now).total_seconds())
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "daily_limit_exceeded",
                    "message": f"Daily upload limit reached. Try again tomorrow or sign up for unlimited uploads.",
                    "retry_after": retry_after,
                    "signup_suggestion": "Sign up for free to get unlimited uploads and advanced features!"
                }
            )
        
        logger.info(
            "Rate limit check passed",
            correlation_id=correlation_id,
            client_ip=client_ip,
            hour_usage=hour_usage,
            day_usage=day_usage
        )
    
    # Database operation methods implementation
    
    async def _upload_file_to_storage(
        self,
        file_content: bytes,
        storage_path: str,
        correlation_id: str
    ) -> str:
        """
        Upload file to Supabase storage.
        
        Args:
            file_content: Raw file bytes
            storage_path: Path in storage bucket
            correlation_id: Request correlation ID
            
        Returns:
            Public URL of uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            logger.info(
                "Uploading file to storage",
                correlation_id=correlation_id,
                storage_path=storage_path,
                file_size=len(file_content)
            )
            
            # Upload to Supabase storage
            upload_response = self.supabase.storage.from_(
                settings.SUPABASE_BUCKET_UPLOADS
            ).upload(
                storage_path,
                file_content,
                {"content-type": "application/octet-stream"}
            )
            
            # Check if upload response has error attribute (new supabase client)
            if hasattr(upload_response, 'error') and upload_response.error:
                raise Exception(f"Storage upload failed: {upload_response.error}")
            # Check if upload response is a dict with error key (old format)
            elif isinstance(upload_response, dict) and upload_response.get("error"):
                raise Exception(f"Storage upload failed: {upload_response['error']}")
            # Check HTTP status code
            elif hasattr(upload_response, 'status_code') and upload_response.status_code >= 400:
                raise Exception(f"Storage upload failed with status {upload_response.status_code}")
            
            # Get public URL
            public_url = self.supabase.storage.from_(
                settings.SUPABASE_BUCKET_UPLOADS
            ).get_public_url(storage_path)
            
            logger.info(
                "File uploaded successfully",
                correlation_id=correlation_id,
                storage_path=storage_path,
                public_url=public_url
            )
            
            return public_url
            
        except Exception as e:
            logger.error(
                "File upload failed",
                correlation_id=correlation_id,
                storage_path=storage_path,
                error=str(e)
            )
            raise
    
    async def _create_session_record(
        self,
        session_data: AnonymousSessionCreate,
        correlation_id: str
    ) -> AnonymousSession:
        """
        Create anonymous session record in database.
        
        Args:
            session_data: Session creation data
            correlation_id: Request correlation ID
            
        Returns:
            Created AnonymousSession
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(
                "Creating session record",
                correlation_id=correlation_id,
                session_token=session_data.session_token[:16] + "..."
            )
            
            # Prepare session data for database
            session_record = {
                "session_token": session_data.session_token,
                "file_name": session_data.file_name,
                "file_size": session_data.file_size,
                "storage_path": session_data.storage_path,
                "status": AnonymousSessionStatus.UPLOADED.value,
                "ip_address": session_data.ip_address,
                "user_agent": session_data.user_agent,
                "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            response = self.supabase.table("anonymous_sessions").insert(
                session_record
            ).execute()
            
            if not response.data:
                raise Exception("Failed to create session record")
            
            session = AnonymousSession(**response.data[0])
            
            logger.info(
                "Session record created",
                correlation_id=correlation_id,
                session_id=session.id
            )
            
            return session
            
        except Exception as e:
            logger.error(
                "Session record creation failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise
    
    async def _create_anonymous_project(
        self,
        session_id: str,
        project_name: str,
        description: Optional[str],
        language: Optional[str],
        file_size: int,
        correlation_id: str
    ) -> str:
        """
        Create anonymous project record.
        
        Args:
            session_id: Anonymous session ID
            project_name: User-provided project name
            description: Optional description
            language: Language code
            file_size: File size in bytes
            correlation_id: Request correlation ID
            
        Returns:
            Created project ID
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(
                "Creating anonymous project",
                correlation_id=correlation_id,
                session_id=session_id,
                project_name=project_name
            )
            
            project_id = str(uuid.uuid4())
            
            # Prepare project data
            project_record = {
                "id": project_id,
                "user_id": None,  # Anonymous project
                "anonymous_session_id": session_id,
                "title": project_name,
                "description": description,
                "status": "uploading",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            response = self.supabase.table("projects").insert(
                project_record
            ).execute()
            
            if not response.data:
                raise Exception("Failed to create project record")
            
            logger.info(
                "Anonymous project created",
                correlation_id=correlation_id,
                project_id=project_id
            )
            
            return project_id
            
        except Exception as e:
            logger.error(
                "Anonymous project creation failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise
    
    async def _update_session_project(
        self,
        session_id: str,
        project_id: str,
        correlation_id: str
    ) -> None:
        """
        Update session with project ID.
        
        Args:
            session_id: Session ID to update
            project_id: Project ID to associate
            correlation_id: Request correlation ID
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(
                "Updating session with project ID",
                correlation_id=correlation_id,
                session_id=session_id,
                project_id=project_id
            )
            
            # Update session record
            response = self.supabase.table("anonymous_sessions").update({
                "project_id": project_id,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", session_id).execute()
            
            if not response.data:
                raise Exception("Failed to update session with project ID")
            
            logger.info(
                "Session updated with project ID",
                correlation_id=correlation_id,
                session_id=session_id,
                project_id=project_id
            )
            
        except Exception as e:
            logger.error(
                "Session project update failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise
    
    async def _start_transcription_job(
        self,
        project_id: str,
        storage_path: str,
        session_token: str,
        language: Optional[str],
        correlation_id: str
    ) -> int:
        """
        Start background transcription job.
        
        Args:
            project_id: Project ID
            storage_path: File storage path
            session_token: Session token for updates
            language: Language code
            correlation_id: Request correlation ID
            
        Returns:
            Estimated processing time in seconds
            
        Raises:
            Exception: If job submission fails
        """
        try:
            logger.info(
                "Starting transcription job",
                correlation_id=correlation_id,
                project_id=project_id,
                storage_path=storage_path
            )
            
            # Submit transcription task to background service
            task_id = background_service.submit_anonymous_transcription_task(
                project_id=project_id,
                storage_path=storage_path,
                session_token=session_token,
                language=language or "en"
            )
            
            # Update project status
            await self._update_project_status(
                project_id, "processing", correlation_id
            )
            
            # Estimate processing time (rough calculation)
            estimated_time = 45  # Default estimate for anonymous uploads
            
            logger.info(
                "Transcription job started",
                correlation_id=correlation_id,
                task_id=task_id,
                estimated_time=estimated_time
            )
            
            return estimated_time
            
        except Exception as e:
            logger.error(
                "Transcription job start failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            # Update project status to failed
            try:
                await self._update_project_status(
                    project_id, "failed", correlation_id
                )
            except:
                pass
            raise
    
    async def _update_project_status(
        self,
        project_id: str,
        status: str,
        correlation_id: str
    ) -> None:
        """
        Update project status.
        
        Args:
            project_id: Project ID to update
            status: New status
            correlation_id: Request correlation ID
        """
        try:
            response = self.supabase.table("projects").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            logger.info(
                "Project status updated",
                correlation_id=correlation_id,
                project_id=project_id,
                status=status
            )
            
        except Exception as e:
            logger.error(
                "Project status update failed",
                correlation_id=correlation_id,
                project_id=project_id,
                status=status,
                error=str(e)
            )
    
    async def _track_anonymous_usage(
        self,
        client_ip: Optional[str],
        correlation_id: str
    ) -> None:
        """
        Track anonymous usage for rate limiting.
        
        Args:
            client_ip: Client IP address
            correlation_id: Request correlation ID
        """
        try:
            if not client_ip:
                return
            
            # Track usage in database or cache
            usage_record = {
                "user_id": f"anonymous_{client_ip}",
                "resource_type": "anonymous_upload",
                "credits_used": 1,
                "metadata": {
                    "ip_address": client_ip,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("usage_tracking").insert(usage_record).execute()
            
            logger.info(
                "Anonymous usage tracked",
                correlation_id=correlation_id,
                client_ip=client_ip
            )
            
        except Exception as e:
            logger.warning(
                "Usage tracking failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            # Don't fail the request if usage tracking fails
    
    async def _get_session_by_token(
        self,
        session_token: str,
        correlation_id: str
    ) -> AnonymousSession:
        """
        Get session by token.
        
        Args:
            session_token: Session token
            correlation_id: Request correlation ID
            
        Returns:
            AnonymousSession object
            
        Raises:
            HTTPException: If session not found
        """
        try:
            logger.info(
                "Getting session by token",
                correlation_id=correlation_id,
                session_token=session_token[:16] + "..."
            )
            
            response = self.supabase.table("anonymous_sessions").select("*").eq(
                "session_token", session_token
            ).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "session_not_found",
                        "message": "Session token not found or invalid.",
                        "signup_suggestion": "Sign up to create an account and manage your transcriptions!"
                    }
                )
            
            session = AnonymousSession(**response.data[0])
            
            logger.info(
                "Session retrieved",
                correlation_id=correlation_id,
                session_id=session.id,
                status=session.status
            )
            
            return session
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Session retrieval failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "session_retrieval_failed",
                    "message": "Failed to retrieve session. Please try again.",
                    "correlation_id": correlation_id
                }
            )
    
    async def _get_transcription_progress(
        self,
        project_id: Optional[str],
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Get transcription progress for project.
        
        Args:
            project_id: Project ID
            correlation_id: Request correlation ID
            
        Returns:
            Progress information dictionary
        """
        try:
            if not project_id:
                return {"progress_percentage": None, "estimated_time_remaining": None}
            
            # Check project status
            response = self.supabase.table("projects").select("*").eq(
                "id", project_id
            ).execute()
            
            if not response.data:
                return {"progress_percentage": None, "estimated_time_remaining": None}
            
            project = response.data[0]
            status = project.get("status", "unknown")
            
            # Estimate progress based on status and time elapsed
            created_at = datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))
            elapsed_seconds = (datetime.utcnow().replace(tzinfo=created_at.tzinfo) - created_at).total_seconds()
            
            if status == "processing":
                # Rough progress estimation
                progress = min(90, int(elapsed_seconds / 60 * 30))  # 30% per minute, max 90%
                remaining = max(5, 45 - int(elapsed_seconds))
                return {
                    "progress_percentage": progress,
                    "estimated_time_remaining": remaining
                }
            
            return {"progress_percentage": None, "estimated_time_remaining": None}
            
        except Exception as e:
            logger.warning(
                "Progress check failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return {"progress_percentage": None, "estimated_time_remaining": None}
    
    async def _get_error_message(
        self,
        project_id: Optional[str],
        correlation_id: str
    ) -> Optional[str]:
        """
        Get error message for failed project.
        
        Args:
            project_id: Project ID
            correlation_id: Request correlation ID
            
        Returns:
            Error message if available
        """
        try:
            if not project_id:
                return None
            
            response = self.supabase.table("projects").select("error_message").eq(
                "id", project_id
            ).execute()
            
            if response.data:
                return response.data[0].get("error_message")
            
            return None
            
        except Exception as e:
            logger.warning(
                "Error message retrieval failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return "Processing failed due to an unknown error"
    
    async def _get_transcription_by_session(
        self,
        session_id: str,
        correlation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get transcription data by session ID.
        
        Args:
            session_id: Session ID
            correlation_id: Request correlation ID
            
        Returns:
            Transcription data dictionary
        """
        try:
            response = self.supabase.table("transcriptions").select("*").eq(
                "anonymous_session_id", session_id
            ).execute()
            
            if response.data:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(
                "Transcription retrieval failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return None
    
    async def _claim_session_atomic(
        self,
        session_token: str,
        user_id: str,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Claim session using database function for atomicity.
        
        Args:
            session_token: Session token to claim
            user_id: User ID claiming the session
            correlation_id: Request correlation ID
            
        Returns:
            Result dictionary from database function
        """
        try:
            logger.info(
                "Claiming session atomically",
                correlation_id=correlation_id,
                session_token=session_token[:16] + "...",
                user_id=user_id
            )
            
            # Call database function for atomic claim
            response = self.supabase.rpc(
                "claim_anonymous_session",
                {
                    "p_session_token": session_token,
                    "p_user_id": user_id
                }
            ).execute()
            
            if not response.data:
                raise Exception("Database function returned no data")
            
            result = response.data
            
            logger.info(
                "Session claim result",
                correlation_id=correlation_id,
                success=result.get("success"),
                error=result.get("error")
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Atomic session claim failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return {
                "success": False,
                "error": f"Claim operation failed: {str(e)}"
            }
    
    async def _get_project_data(
        self,
        project_id: str,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Get complete project data.
        
        Args:
            project_id: Project ID
            correlation_id: Request correlation ID
            
        Returns:
            Project data dictionary
        """
        try:
            response = self.supabase.table("projects").select("*").eq(
                "id", project_id
            ).execute()
            
            if response.data:
                return response.data[0]
            
            return {}
            
        except Exception as e:
            logger.error(
                "Project data retrieval failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return {}
    
    async def _get_transcription_data(
        self,
        transcription_id: str,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Get complete transcription data.
        
        Args:
            transcription_id: Transcription ID
            correlation_id: Request correlation ID
            
        Returns:
            Transcription data dictionary
        """
        try:
            response = self.supabase.table("transcriptions").select("*").eq(
                "id", transcription_id
            ).execute()
            
            if response.data:
                return response.data[0]
            
            return {}
            
        except Exception as e:
            logger.error(
                "Transcription data retrieval failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return {}
    
    async def _get_hourly_usage(self, client_ip: str) -> int:
        """
        Get hourly upload count for IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Number of uploads in current hour
        """
        try:
            hour_start = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            
            response = self.supabase.table("usage_tracking").select("id").eq(
                "user_id", f"anonymous_{client_ip}"
            ).eq("resource_type", "anonymous_upload").gte(
                "created_at", hour_start.isoformat()
            ).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            logger.warning(f"Hourly usage check failed: {e}")
            return self.usage_limits.max_uploads_per_hour  # Conservative fallback
    
    async def _get_daily_usage(self, client_ip: str) -> int:
        """
        Get daily upload count for IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Number of uploads in current day
        """
        try:
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            response = self.supabase.table("usage_tracking").select("id").eq(
                "user_id", f"anonymous_{client_ip}"
            ).eq("resource_type", "anonymous_upload").gte(
                "created_at", day_start.isoformat()
            ).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            logger.warning(f"Daily usage check failed: {e}")
            return self.usage_limits.max_uploads_per_day  # Conservative fallback