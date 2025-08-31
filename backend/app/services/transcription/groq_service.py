"""
Groq Transcription Service
Handles audio/video transcription using Groq's Whisper API
"""

import os
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
import aiofiles
from groq import Groq
from loguru import logger

from app.core.config import settings


class GroqTranscriptionService:
    """Service for transcribing audio using Groq's Whisper API."""
    
    def __init__(self):
        """Initialize Groq client with API key from settings."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.max_file_size = settings.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.model = settings.GROQ_MODEL
        
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        response_format: str = "verbose_json"
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file using Groq's Whisper API.
        
        Args:
            file_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            response_format: Format of response ('json', 'text', 'srt', 'verbose_json', 'vtt')
            
        Returns:
            Dictionary containing transcription results
            
        Raises:
            ValueError: If file is too large or invalid format
            Exception: For API errors
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                logger.warning(f"File too large: {file_size} bytes. Max: {self.max_file_size} bytes")
                # In production, implement compression or chunking here
                raise ValueError(f"File size {file_size/1024/1024:.2f}MB exceeds maximum {settings.MAX_AUDIO_FILE_SIZE_MB}MB")
            
            logger.info(f"Starting transcription for file: {file_path} ({file_size/1024/1024:.2f}MB)")
            
            # Open and transcribe file
            with open(file_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.model,
                    response_format=response_format,
                    language=language,
                    temperature=0.0  # Use 0 for consistency
                )
            
            # Process response based on format
            if response_format == "verbose_json":
                result = {
                    "text": transcription.text,
                    "language": transcription.language,
                    "duration": transcription.duration,
                    "segments": transcription.segments,
                    "provider": "groq",
                    "model": self.model
                }
            else:
                result = {
                    "text": transcription.text if hasattr(transcription, 'text') else str(transcription),
                    "provider": "groq",
                    "model": self.model,
                    "language": language or "auto-detected"
                }
            
            # Calculate word count
            result["word_count"] = len(result["text"].split()) if result.get("text") else 0
            
            logger.info(f"Transcription completed. Words: {result['word_count']}, Language: {result.get('language', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise
    
    async def transcribe_from_supabase(
        self,
        storage_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download file from Supabase storage and transcribe it.
        
        Args:
            storage_path: Path in Supabase storage
            language: Optional language code
            
        Returns:
            Transcription results
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
            result = await self.transcribe_file(tmp_path, language)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to transcribe from Supabase: {str(e)}")
            # Clean up temp file if it exists
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    
    def estimate_processing_time(self, duration_seconds: float) -> float:
        """
        Estimate processing time based on audio duration.
        Groq is typically very fast, processing at 10-20x real-time.
        
        Args:
            duration_seconds: Duration of audio in seconds
            
        Returns:
            Estimated processing time in seconds
        """
        # Groq typically processes at 10-20x speed
        # We'll be conservative and estimate 10x
        return max(duration_seconds / 10, 5.0)  # Minimum 5 seconds
