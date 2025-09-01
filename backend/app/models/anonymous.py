"""
Anonymous Session Models
Pydantic models for anonymous upload functionality
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class AnonymousSessionStatus(str, Enum):
    """Status values for anonymous sessions"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CLAIMED = "claimed"


class AnonymousUploadRequest(BaseModel):
    """Request model for anonymous file upload"""
    name: str = Field(..., description="Project name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Optional project description", max_length=500)
    language: Optional[str] = Field("en", description="Language code (ISO 639-1)", max_length=5)


class AnonymousUploadResponse(BaseModel):
    """Response from anonymous file upload"""
    session_token: str = Field(..., description="Unique session token for accessing results")
    project_id: str = Field(..., description="Generated project ID")
    file_name: str = Field(..., description="Uploaded file name")
    file_size: int = Field(..., description="File size in bytes")
    status: AnonymousSessionStatus = Field(..., description="Current processing status")
    estimated_time_seconds: int = Field(..., description="Estimated processing time")
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    message: str = Field(..., description="Human-readable status message")


class AnonymousStatusResponse(BaseModel):
    """Response for anonymous session status check"""
    session_token: str = Field(..., description="Session token")
    status: AnonymousSessionStatus = Field(..., description="Current processing status")
    progress_percentage: Optional[int] = Field(None, description="Processing progress (0-100)", ge=0, le=100)
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated seconds remaining")
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Upload timestamp")
    expires_at: datetime = Field(..., description="Session expiration")
    is_expired: bool = Field(..., description="Whether session has expired")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")


class TranscriptionPreview(BaseModel):
    """Preview of transcription results (blurred)"""
    preview_text: str = Field(..., description="First portion of transcription (unblurred)")
    total_word_count: int = Field(..., description="Total words in full transcription")
    duration_seconds: float = Field(..., description="Audio duration")
    language: str = Field(..., description="Detected/specified language")
    confidence: Optional[float] = Field(None, description="Overall confidence score", ge=0, le=1)
    processing_time_ms: Optional[int] = Field(None, description="Time taken to process")


class AnonymousResultResponse(BaseModel):
    """Response for anonymous transcription results (blurred)"""
    session_token: str = Field(..., description="Session token")
    status: AnonymousSessionStatus = Field(..., description="Processing status")
    transcription_preview: Optional[TranscriptionPreview] = Field(None, description="Blurred transcription preview")
    is_blurred: bool = Field(True, description="Whether content is blurred/limited")
    signup_required: bool = Field(True, description="Whether signup is required to view full content")
    expires_at: datetime = Field(..., description="Session expiration")
    conversion_message: str = Field(..., description="Call-to-action message for signup")
    
    # Metadata for conversion optimization
    file_info: Dict[str, Any] = Field(default_factory=dict, description="File metadata for display")
    usage_stats: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics for social proof")


class ClaimSessionRequest(BaseModel):
    """Request to claim an anonymous session"""
    # No additional fields needed - user info comes from JWT
    pass


class ClaimSessionResponse(BaseModel):
    """Response from claiming an anonymous session"""
    success: bool = Field(..., description="Whether claim was successful")
    project_id: Optional[str] = Field(None, description="Project ID if successful")
    transcription_id: Optional[str] = Field(None, description="Transcription ID if successful")
    full_content: Optional[str] = Field(None, description="Full transcription content")
    claimed_at: Optional[datetime] = Field(None, description="When session was claimed")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    
    # Additional data for frontend
    project_data: Optional[Dict[str, Any]] = Field(None, description="Complete project information")
    transcription_data: Optional[Dict[str, Any]] = Field(None, description="Complete transcription information")


class AnonymousSession(BaseModel):
    """Core anonymous session model"""
    id: str = Field(..., description="Session UUID")
    session_token: str = Field(..., description="Unique access token")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    transcription_id: Optional[str] = Field(None, description="Associated transcription ID")
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    storage_path: str = Field(..., description="Storage path in bucket")
    status: AnonymousSessionStatus = Field(..., description="Current status")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    expires_at: datetime = Field(..., description="Session expiration")
    claimed_by_user_id: Optional[str] = Field(None, description="User ID if claimed")
    claimed_at: Optional[datetime] = Field(None, description="When claimed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AnonymousSessionCreate(BaseModel):
    """Model for creating new anonymous session"""
    session_token: str = Field(..., description="Generated session token")
    file_name: str = Field(..., description="Uploaded file name")
    file_size: int = Field(..., description="File size in bytes")
    storage_path: str = Field(..., description="Storage path")
    ip_address: Optional[str] = Field(None, description="Client IP")
    user_agent: Optional[str] = Field(None, description="Client user agent")


class AnonymousUsageLimits(BaseModel):
    """Usage limits for anonymous users"""
    max_uploads_per_hour: int = Field(999, description="Maximum uploads per hour")
    max_uploads_per_day: int = Field(999, description="Maximum uploads per day")
    max_file_size_mb: int = Field(25, description="Maximum file size in MB")
    max_duration_minutes: int = Field(60, description="Maximum audio duration in minutes")
    allowed_file_types: List[str] = Field(
        default=[".mp3", ".wav", ".m4a", ".aac", ".ogg"],
        description="Allowed file extensions"
    )


class AnonymousRateLimitInfo(BaseModel):
    """Rate limit information for anonymous users"""
    uploads_used_hour: int = Field(..., description="Uploads used in current hour")
    uploads_used_day: int = Field(..., description="Uploads used in current day")
    uploads_remaining_hour: int = Field(..., description="Uploads remaining this hour")
    uploads_remaining_day: int = Field(..., description="Uploads remaining today")
    reset_time_hour: datetime = Field(..., description="When hourly limit resets")
    reset_time_day: datetime = Field(..., description="When daily limit resets")
    is_limited: bool = Field(..., description="Whether user is currently rate limited")


class AnonymousErrorResponse(BaseModel):
    """Error response for anonymous endpoints"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    session_token: Optional[str] = Field(None, description="Session token if applicable")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")
    
    # Conversion opportunities even in errors
    signup_suggestion: Optional[str] = Field(None, description="Suggestion to sign up for more features")


# Utility functions for model validation and conversion

def create_conversion_message(transcription_preview: TranscriptionPreview) -> str:
    """Generate compelling conversion message based on transcription data"""
    word_count = transcription_preview.total_word_count
    duration_minutes = round(transcription_preview.duration_seconds / 60)
    
    return (
        f"Your {duration_minutes}-minute audio has been transcribed into {word_count:,} words. "
        f"Sign up free to view the complete transcription and unlock powerful repurposing features!"
    )


def create_file_info_metadata(file_name: str, file_size: int, duration_seconds: float) -> Dict[str, Any]:
    """Create file metadata for display in conversion overlay"""
    return {
        "file_name": file_name,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "duration_minutes": round(duration_seconds / 60, 1),
        "estimated_reading_time": round(duration_seconds / 60 * 0.3),  # Rough estimate
    }


def create_usage_stats_metadata() -> Dict[str, Any]:
    """Create usage statistics for social proof"""
    return {
        "total_users": "10,000+",
        "files_processed_today": "247",
        "average_satisfaction": "4.9/5",
        "time_saved_hours": "15,000+",
    }


def generate_preview_text(full_content: str, preview_length: int = 150) -> str:
    """Generate preview text from full transcription"""
    if len(full_content) <= preview_length:
        return full_content
    
    # Find a good breaking point (end of sentence or word)
    preview = full_content[:preview_length]
    
    # Try to break at sentence end
    last_period = preview.rfind('.')
    if last_period > preview_length * 0.7:  # If period is reasonably close to end
        return preview[:last_period + 1]
    
    # Otherwise break at word boundary
    last_space = preview.rfind(' ')
    if last_space > 0:
        return preview[:last_space] + "..."
    
    return preview + "..."