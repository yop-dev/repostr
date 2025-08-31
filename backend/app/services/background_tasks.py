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
