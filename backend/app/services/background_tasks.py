"""
Background Task Service
Handles asynchronous task processing for transcription
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from app.services.transcription import TranscriptionManager
from app.api.deps import get_supabase_client
from app.core.config import settings


class BackgroundTaskService:
    """Service for managing background tasks."""
    
    def __init__(self):
        """Initialize background task service."""
        self.transcription_manager = TranscriptionManager()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.tasks = {}  # Track running tasks
    
    async def process_transcription(
        self,
        project_id: str,
        storage_path: str,
        user_id: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process transcription in the background.
        
        Args:
            project_id: Project ID
            storage_path: Path to file in Supabase storage
            user_id: User ID
            language: Optional language code
            
        Returns:
            Transcription result
        """
        supabase = get_supabase_client()
        start_time = datetime.utcnow()
        
        try:
            # Update project status to processing
            logger.info(f"Starting transcription for project {project_id}")
            supabase.table("projects").update({
                "status": "processing",
                "transcription_status": "processing",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            # Perform transcription
            result = await self.transcription_manager.transcribe_from_supabase(
                storage_path=storage_path,
                language=language,
                project_id=project_id
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Save transcription to database
            transcription_data = {
                "project_id": project_id,
                "user_id": user_id,
                "text": result["text"],
                "language": result.get("language", language or "auto"),
                "duration": result.get("file_info", {}).get("duration"),
                "word_count": result["word_count"],
                "segments": result.get("segments"),
                "provider": result["provider"],
                "model": result["model"],
                "chunks_processed": result.get("chunks_processed"),
                "processing_time_seconds": processing_time,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            transcription_response = supabase.table("transcriptions").insert(
                transcription_data
            ).execute()
            
            transcription_id = transcription_response.data[0]["id"]
            
            # Update project with transcription info
            supabase.table("projects").update({
                "status": "completed",
                "transcription_status": "completed",
                "transcription_id": transcription_id,
                "duration_seconds": result.get("file_info", {}).get("duration"),
                "transcribed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            logger.info(f"Transcription completed for project {project_id} in {processing_time:.1f}s")
            
            return {
                "success": True,
                "transcription_id": transcription_id,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Transcription failed for project {project_id}: {str(e)}")
            
            # Update project status to failed
            supabase.table("projects").update({
                "status": "failed",
                "transcription_status": "failed",
                "transcription_error": str(e),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_anonymous_transcription(
        self,
        project_id: str,
        storage_path: str,
        session_token: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process anonymous transcription in the background.
        
        Args:
            project_id: Project ID
            storage_path: Path to file in Supabase storage
            session_token: Anonymous session token
            language: Optional language code
            
        Returns:
            Transcription result
        """
        supabase = get_supabase_client()
        start_time = datetime.utcnow()
        correlation_id = f"anon_transcription_{project_id}"
        
        try:
            logger.info(
                "Starting anonymous transcription",
                correlation_id=correlation_id,
                project_id=project_id,
                session_token=session_token[:16] + "..."
            )
            
            # Get session info
            session_response = supabase.table("anonymous_sessions").select("*").eq(
                "session_token", session_token
            ).execute()
            
            if not session_response.data:
                raise Exception("Anonymous session not found")
            
            session = session_response.data[0]
            session_id = session["id"]
            
            # Update session and project status to processing
            supabase.table("anonymous_sessions").update({
                "status": "processing",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", session_id).execute()
            
            supabase.table("projects").update({
                "status": "processing",
                "processing_started_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            # Perform transcription
            result = await self.transcription_manager.transcribe_from_supabase(
                storage_path=storage_path,
                language=language,
                project_id=project_id
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Save transcription to database with anonymous session reference
            # Use only the columns that exist in the current schema
            transcription_data = {
                "project_id": project_id,  # Required field
                "user_id": None,  # Anonymous transcription
                "anonymous_session_id": session_id,  # session_id is the UUID from the session record
                "text": result["text"],  # Column is called 'text', not 'content'
                "language": result.get("language", language or "en"),
                "word_count": result["word_count"],
                "provider": result["provider"],
                "model": result.get("model", "whisper-large-v3")  # Required field
            }
            
            # Add segments if available
            if result.get("segments"):
                transcription_data["segments"] = result["segments"]
            
            transcription_response = supabase.table("transcriptions").insert(
                transcription_data
            ).execute()
            
            if not transcription_response.data:
                raise Exception("Failed to save transcription")
            
            transcription_id = transcription_response.data[0]["id"]
            
            # Update session with transcription info
            supabase.table("anonymous_sessions").update({
                "transcription_id": transcription_id,
                "status": "completed",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", session_id).execute()
            
            # Update project status
            supabase.table("projects").update({
                "status": "completed",
                "processing_completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", project_id).execute()
            
            logger.info(
                "Anonymous transcription completed",
                correlation_id=correlation_id,
                project_id=project_id,
                transcription_id=transcription_id,
                processing_time=processing_time,
                word_count=result["word_count"]
            )
            
            return {
                "success": True,
                "transcription_id": transcription_id,
                "session_id": session_id,
                "processing_time": processing_time,
                "word_count": result["word_count"]
            }
            
        except Exception as e:
            logger.error(
                "Anonymous transcription failed",
                correlation_id=correlation_id,
                project_id=project_id,
                error=str(e),
                exc_info=True
            )
            
            # Update session and project status to failed
            try:
                # Get session ID if we don't have it
                if 'session_id' not in locals():
                    session_response = supabase.table("anonymous_sessions").select("id").eq(
                        "session_token", session_token
                    ).execute()
                    if session_response.data:
                        session_id = session_response.data[0]["id"]
                    else:
                        session_id = None
                
                if session_id:
                    supabase.table("anonymous_sessions").update({
                        "status": "failed",
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", session_id).execute()
                
                supabase.table("projects").update({
                    "status": "failed",
                    "error_message": str(e),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", project_id).execute()
                
            except Exception as update_error:
                logger.error(
                    "Failed to update failure status",
                    correlation_id=correlation_id,
                    error=str(update_error)
                )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def submit_transcription_task(
        self,
        project_id: str,
        storage_path: str,
        user_id: str,
        language: Optional[str] = None
    ) -> str:
        """
        Submit a transcription task to run in the background.
        
        Args:
            project_id: Project ID
            storage_path: Path to file in Supabase storage
            user_id: User ID
            language: Optional language code
            
        Returns:
            Task ID
        """
        task_id = f"transcription_{project_id}"
        
        # Create async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        future = self.executor.submit(
            loop.run_until_complete,
            self.process_transcription(project_id, storage_path, user_id, language)
        )
        
        self.tasks[task_id] = future
        
        logger.info(f"Submitted transcription task {task_id}")
        return task_id
    
    def submit_anonymous_transcription_task(
        self,
        project_id: str,
        storage_path: str,
        session_token: str,
        language: Optional[str] = None
    ) -> str:
        """
        Submit an anonymous transcription task to run in the background.
        
        Args:
            project_id: Project ID
            storage_path: Path to file in Supabase storage
            session_token: Anonymous session token
            language: Optional language code
            
        Returns:
            Task ID
        """
        task_id = f"anonymous_transcription_{project_id}"
        
        # Create async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        future = self.executor.submit(
            loop.run_until_complete,
            self.process_anonymous_transcription(project_id, storage_path, session_token, language)
        )
        
        self.tasks[task_id] = future
        
        logger.info(
            "Submitted anonymous transcription task",
            task_id=task_id,
            project_id=project_id,
            session_token=session_token[:16] + "..."
        )
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a background task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        if task_id not in self.tasks:
            return {"status": "not_found"}
        
        future = self.tasks[task_id]
        
        if future.done():
            try:
                result = future.result()
                return {
                    "status": "completed",
                    "result": result
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e)
                }
        else:
            return {"status": "running"}
    
    def get_anonymous_task_status(self, session_token: str) -> Dict[str, Any]:
        """
        Get status of an anonymous transcription task by session token.
        
        Args:
            session_token: Anonymous session token
            
        Returns:
            Task status information with session context
        """
        # Try to find task by session token
        task_id = None
        for tid in self.tasks.keys():
            if tid.startswith("anonymous_transcription_") and session_token[:16] in tid:
                task_id = tid
                break
        
        if not task_id:
            # Check database for session status
            try:
                supabase = get_supabase_client()
                session_response = supabase.table("anonymous_sessions").select(
                    "status, created_at, updated_at"
                ).eq("session_token", session_token).execute()
                
                if session_response.data:
                    session = session_response.data[0]
                    return {
                        "status": session["status"],
                        "database_status": True,
                        "created_at": session["created_at"],
                        "updated_at": session["updated_at"]
                    }
                else:
                    return {"status": "session_not_found"}
            except Exception as e:
                logger.error(f"Failed to check session status: {e}")
                return {"status": "error", "error": str(e)}
        
        # Get task status
        return self.get_task_status(task_id)
    
    async def update_anonymous_session_status(
        self,
        session_token: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update anonymous session status in database.
        
        Args:
            session_token: Session token
            status: New status
            error_message: Optional error message
            
        Returns:
            Success status
        """
        try:
            supabase = get_supabase_client()
            
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            response = supabase.table("anonymous_sessions").update(
                update_data
            ).eq("session_token", session_token).execute()
            
            if response.data:
                logger.info(
                    "Anonymous session status updated",
                    session_token=session_token[:16] + "...",
                    status=status
                )
                return True
            else:
                logger.warning(
                    "Failed to update anonymous session status",
                    session_token=session_token[:16] + "...",
                    status=status
                )
                return False
                
        except Exception as e:
            logger.error(
                "Error updating anonymous session status",
                session_token=session_token[:16] + "...",
                status=status,
                error=str(e)
            )
            return False
    
    def cleanup_completed_tasks(self):
        """Remove completed tasks from tracking."""
        completed = [
            task_id for task_id, future in self.tasks.items()
            if future.done()
        ]
        
        for task_id in completed:
            del self.tasks[task_id]
        
        if completed:
            logger.info(f"Cleaned up {len(completed)} completed tasks")


# Global instance
background_service = BackgroundTaskService()
