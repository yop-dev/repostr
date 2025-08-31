"""
Project and Transcription Models
Database models for managing projects and transcriptions
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Project status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionStatus(str, Enum):
    """Transcription status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectCreate(BaseModel):
    """Project creation request model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^[a-z]{2}$")  # ISO 639-1 code
    tags: Optional[List[str]] = []


class ProjectUpdate(BaseModel):
    """Project update request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TranscriptionSegment(BaseModel):
    """Transcription segment with timestamp."""
    id: int
    start: float
    end: float
    text: str
    confidence: Optional[float] = None


class TranscriptionResult(BaseModel):
    """Transcription result model."""
    text: str
    language: str
    duration: Optional[float] = None
    word_count: int
    segments: Optional[List[TranscriptionSegment]] = None
    provider: str
    model: str
    chunks_processed: Optional[int] = None


class Project(BaseModel):
    """Project model."""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    language: Optional[str] = None
    tags: List[str] = []
    
    # File info
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_url: Optional[str] = None
    storage_path: Optional[str] = None
    
    # Audio info
    duration_seconds: Optional[float] = None
    
    # Transcription
    transcription_id: Optional[str] = None
    transcription_status: Optional[TranscriptionStatus] = None
    transcription_error: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    transcribed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Transcription(BaseModel):
    """Transcription model."""
    id: str
    project_id: str
    user_id: str
    
    # Transcription content
    text: str
    language: str
    duration: Optional[float] = None
    word_count: int
    
    # Segments with timestamps
    segments: Optional[List[Dict[str, Any]]] = None
    
    # Provider info
    provider: str
    model: str
    
    # Processing info
    chunks_processed: Optional[int] = None
    processing_time_seconds: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileUploadResponse(BaseModel):
    """File upload response model."""
    project_id: str
    file_name: str
    file_size: int
    storage_path: str
    upload_url: Optional[str] = None
    message: str


class TranscriptionJobResponse(BaseModel):
    """Transcription job response model."""
    project_id: str
    transcription_id: Optional[str] = None
    status: TranscriptionStatus
    message: str
    estimated_time_seconds: Optional[float] = None


class ProjectWithTranscription(BaseModel):
    """Project with full transcription data."""
    project: Project
    transcription: Optional[Transcription] = None
    
    
class ProjectListResponse(BaseModel):
    """Project list response."""
    projects: List[Project]
    total: int
    page: int
    per_page: int
    has_more: bool


class UserUsageStats(BaseModel):
    """User usage statistics for tier limits."""
    projects_this_month: int
    monthly_limit: int
    total_projects: int
    total_duration_minutes: float
    tier: str = "free"
