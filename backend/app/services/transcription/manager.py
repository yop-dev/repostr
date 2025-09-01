"""
Transcription Manager
Orchestrates the transcription process with provider fallback and chunking support
"""

import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import tempfile
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.services.transcription.groq_service import GroqTranscriptionService
try:
    from app.services.transcription.audio_utils import AudioProcessor
except (ImportError, ModuleNotFoundError):
    # Fallback for Python 3.13+ where pydub doesn't work
    try:
        from app.services.transcription.audio_utils_minimal import AudioProcessor
    except ImportError:
        from app.services.transcription.audio_utils_stub import AudioProcessor


class TranscriptionProvider(str, Enum):
    """Available transcription providers."""
    GROQ = "groq"
    OPENAI = "openai"  # For future implementation


class TranscriptionStatus(str, Enum):
    """Transcription job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionManager:
    """
    Manages transcription workflow including:
    - Provider selection and fallback
    - File processing (compression/chunking)
    - Rate limiting
    - Error handling
    """
    
    def __init__(self):
        """Initialize transcription manager with configured providers."""
        self.audio_processor = AudioProcessor()
        self.primary_provider = settings.TRANSCRIPTION_PROVIDER
        
        # Initialize providers
        self.providers = {}
        if settings.GROQ_API_KEY:
            self.providers[TranscriptionProvider.GROQ] = GroqTranscriptionService()
        
        # Rate limiting settings
        self.rate_limit_requests = settings.TRANSCRIPTION_RATE_LIMIT_REQUESTS
        self.rate_limit_window = settings.TRANSCRIPTION_RATE_LIMIT_WINDOW
        
        # Track request times for rate limiting
        self.request_times = []
    
    async def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        provider: Optional[TranscriptionProvider] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main transcription method with automatic handling of large files.
        
        Args:
            file_path: Path to audio/video file
            language: Optional language code
            provider: Optional provider override
            project_id: Optional project ID for tracking
            
        Returns:
            Transcription result dictionary
        """
        try:
            # Validate file
            self.audio_processor.validate_file(file_path)
            
            # Select provider
            selected_provider = provider or self.primary_provider
            if selected_provider not in self.providers:
                raise ValueError(f"Provider {selected_provider} not available")
            
            # Check rate limits
            await self._check_rate_limit()
            
            # Get file info (fallback if FFmpeg not available)
            try:
                file_info = self.audio_processor.get_audio_info(file_path)
                logger.info(f"Starting transcription for {file_path}")
                logger.info(f"File info: {file_info['duration']:.1f}s, {file_info['size_mb']:.2f}MB")
                
                # Prepare file (handle compression/chunking if needed)
                files_to_process, needs_merging = await self.audio_processor.prepare_file_for_transcription(file_path)
            except FileNotFoundError as e:
                if 'ffprobe' in str(e) or 'ffmpeg' in str(e):
                    logger.warning("FFmpeg not available, using direct transcription")
                    # Fallback: use file directly without processing
                    file_size = Path(file_path).stat().st_size
                    file_info = {
                        'duration': 0,  # Unknown duration
                        'size_mb': file_size / (1024 * 1024),
                        'format': Path(file_path).suffix.lower()
                    }
                    files_to_process = [file_path]
                    needs_merging = False
                    logger.info(f"Starting direct transcription for {file_path} ({file_info['size_mb']:.2f}MB)")
                else:
                    raise
            
            # Process transcription
            if needs_merging:
                # Process chunks
                logger.info(f"Processing {len(files_to_process)} chunks")
                result = await self._process_chunks(
                    files_to_process,
                    selected_provider,
                    language
                )
                
                # Clean up chunk files
                self.audio_processor.cleanup_temp_files(files_to_process)
            else:
                # Process single file
                result = await self._transcribe_single(
                    files_to_process[0],
                    selected_provider,
                    language
                )
                
                # Clean up if it was a compressed file
                if files_to_process[0] != file_path:
                    self.audio_processor.cleanup_temp_files(files_to_process)
            
            # Add metadata
            result["file_info"] = file_info
            result["project_id"] = project_id
            result["transcribed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Transcription completed: {result.get('word_count', 0)} words")
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            
            # Try fallback provider if available
            if selected_provider == TranscriptionProvider.GROQ and TranscriptionProvider.OPENAI in self.providers:
                logger.info("Attempting fallback to OpenAI provider")
                return await self.transcribe(
                    file_path,
                    language,
                    TranscriptionProvider.OPENAI,
                    project_id
                )
            
            raise
    
    async def _transcribe_single(
        self,
        file_path: str,
        provider: TranscriptionProvider,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe a single file with the specified provider.
        
        Args:
            file_path: Path to audio file
            provider: Transcription provider to use
            language: Optional language code
            
        Returns:
            Transcription result
        """
        service = self.providers[provider]
        
        # Record request time for rate limiting
        self.request_times.append(datetime.utcnow())
        
        # Perform transcription
        result = await service.transcribe_file(file_path, language)
        
        return result
    
    async def _process_chunks(
        self,
        chunk_files: List[str],
        provider: TranscriptionProvider,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process multiple audio chunks and merge results.
        
        Args:
            chunk_files: List of chunk file paths
            provider: Transcription provider to use
            language: Optional language code
            
        Returns:
            Merged transcription result
        """
        chunk_results = []
        
        for i, chunk_file in enumerate(chunk_files):
            logger.info(f"Processing chunk {i+1}/{len(chunk_files)}")
            
            # Transcribe chunk
            chunk_result = await self._transcribe_single(
                chunk_file,
                provider,
                language
            )
            
            chunk_results.append(chunk_result)
            
            # Add small delay between chunks to avoid rate limiting
            if i < len(chunk_files) - 1:
                await asyncio.sleep(2)
        
        # Merge all chunk transcriptions
        merged_result = await self.audio_processor.merge_transcriptions(chunk_results)
        
        return merged_result
    
    async def _check_rate_limit(self) -> None:
        """
        Check and enforce rate limiting.
        
        Raises:
            Exception: If rate limit exceeded
        """
        if not self.rate_limit_requests:
            return  # No rate limiting configured
        
        # Clean up old request times
        current_time = datetime.utcnow()
        window_start = current_time.timestamp() - self.rate_limit_window
        
        self.request_times = [
            t for t in self.request_times
            if t.timestamp() > window_start
        ]
        
        # Check if limit exceeded
        if len(self.request_times) >= self.rate_limit_requests:
            wait_time = self.rate_limit_window - (current_time.timestamp() - self.request_times[0].timestamp())
            raise Exception(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds.")
    
    async def transcribe_from_supabase(
        self,
        storage_path: str,
        language: Optional[str] = None,
        provider: Optional[TranscriptionProvider] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download file from Supabase and transcribe it.
        
        Args:
            storage_path: Path in Supabase storage
            language: Optional language code
            provider: Optional provider override
            project_id: Optional project ID for tracking
            
        Returns:
            Transcription result
        """
        from app.api.deps import get_supabase_client
        
        try:
            # Get Supabase client
            supabase = get_supabase_client()
            
            # Download file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(storage_path).suffix) as tmp_file:
                tmp_path = tmp_file.name
                
                # Download from Supabase
                logger.info(f"Downloading file from Supabase: {storage_path}")
                response = supabase.storage.from_(settings.SUPABASE_BUCKET_UPLOADS).download(storage_path)
                
                # Write to temp file
                tmp_file.write(response)
                tmp_file.flush()
            
            # Transcribe the temporary file
            result = await self.transcribe(
                tmp_path,
                language,
                provider,
                project_id
            )
            
            # Add storage path to result
            result["storage_path"] = storage_path
            
            # Clean up temporary file
            self.audio_processor.cleanup_temp_files([tmp_path])
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to transcribe from Supabase: {str(e)}")
            # Clean up temp file if it exists
            if 'tmp_path' in locals():
                self.audio_processor.cleanup_temp_files([tmp_path])
            raise
    
    def get_available_providers(self) -> List[str]:
        """Get list of available transcription providers."""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider: TranscriptionProvider) -> Dict[str, Any]:
        """
        Get information about a specific provider.
        
        Args:
            provider: Provider to get info for
            
        Returns:
            Provider information dictionary
        """
        if provider not in self.providers:
            return {"available": False}
        
        info = {
            "available": True,
            "name": provider.value,
            "max_file_size_mb": settings.MAX_AUDIO_FILE_SIZE_MB,
            "supports_languages": True,
            "supports_timestamps": True
        }
        
        if provider == TranscriptionProvider.GROQ:
            info.update({
                "model": settings.GROQ_MODEL,
                "rate_limit": f"{self.rate_limit_requests} requests per {self.rate_limit_window} seconds"
            })
        
        return info
    
    async def update_transcription_status(
        self,
        transcription_id: str,
        status: str,
        error_message: Optional[str] = None,
        processing_started_at: Optional[datetime] = None,
        processing_completed_at: Optional[datetime] = None
    ) -> None:
        """
        Update transcription status in database.
        
        Args:
            transcription_id: ID of the transcription to update
            status: New status (pending, processing, completed, failed)
            error_message: Optional error message for failed transcriptions
            processing_started_at: Optional processing start time
            processing_completed_at: Optional processing completion time
        """
        from app.api.deps import get_supabase_client
        
        try:
            supabase = get_supabase_client()
            if not supabase:
                logger.warning("Supabase not available, skipping status update")
                return
            
            # Prepare update data
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            if processing_started_at:
                update_data["processing_started_at"] = processing_started_at
                
            if processing_completed_at:
                update_data["processing_completed_at"] = processing_completed_at
            
            # Update in database
            result = supabase.table("transcriptions").update(update_data).eq("id", transcription_id).execute()
            
            if result.data:
                logger.info(f"Updated transcription {transcription_id} status to {status}")
            else:
                logger.warning(f"No transcription found with ID {transcription_id}")
                
        except Exception as e:
            logger.error(f"Failed to update transcription status: {str(e)}")
            # Don't raise exception to avoid breaking the transcription process
    
    async def update_transcription_results(
        self,
        transcription_id: str,
        text: Optional[str] = None,
        language: Optional[str] = None,
        duration: Optional[float] = None,
        word_count: Optional[int] = None,
        status: str = "completed",
        processing_completed_at: Optional[datetime] = None
    ) -> None:
        """
        Update transcription with results from processing.
        
        Args:
            transcription_id: ID of the transcription to update
            text: Transcribed text
            language: Detected language
            duration: Audio duration in seconds
            word_count: Number of words in transcription
            status: Final status (usually 'completed')
            processing_completed_at: Processing completion time
        """
        from app.api.deps import get_supabase_client
        
        try:
            supabase = get_supabase_client()
            if not supabase:
                logger.warning("Supabase not available, skipping results update")
                return
            
            # Prepare update data
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if text:
                update_data["text"] = text
                
            if language:
                update_data["language"] = language
                
            if duration is not None:
                update_data["duration"] = duration
                
            if word_count is not None:
                update_data["word_count"] = word_count
                
            if processing_completed_at:
                update_data["processing_completed_at"] = processing_completed_at
            
            # Update in database
            result = supabase.table("transcriptions").update(update_data).eq("id", transcription_id).execute()
            
            if result.data:
                logger.info(f"Updated transcription {transcription_id} with results: {word_count} words, {duration}s")
            else:
                logger.warning(f"No transcription found with ID {transcription_id}")
                
        except Exception as e:
            logger.error(f"Failed to update transcription results: {str(e)}")
            # Don't raise exception to avoid breaking the transcription process
