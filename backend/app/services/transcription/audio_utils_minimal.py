"""
Minimal Audio Utils - No pydub dependency
Simple audio file handling without advanced processing
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from loguru import logger


class AudioProcessor:
    """Minimal audio processor that works without pydub/ffmpeg."""
    
    def __init__(self):
        """Initialize minimal audio processor."""
        self.supported_formats = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
        self.max_file_size_mb = 25
    
    def validate_file(self, file_path: str) -> None:
        """
        Validate audio file.
        
        Args:
            file_path: Path to audio file
            
        Raises:
            ValueError: If file is invalid
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.2f}MB (max: {self.max_file_size_mb}MB)")
        
        logger.info(f"File validation passed: {file_path} ({file_size_mb:.2f}MB)")
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic audio file information.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with file info
        """
        try:
            file_size = os.path.getsize(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            return {
                'duration': 0,  # Unknown without ffmpeg
                'size_mb': file_size / (1024 * 1024),
                'format': file_ext,
                'channels': 1,  # Assume mono
                'sample_rate': 44100,  # Default assumption
                'bitrate': None
            }
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            raise
    
    async def prepare_file_for_transcription(self, file_path: str) -> Tuple[List[str], bool]:
        """
        Prepare file for transcription (minimal version).
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (files_to_process, needs_merging)
        """
        # In minimal mode, just return the original file
        return [file_path], False
    
    async def merge_transcriptions(self, transcription_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple transcription results.
        
        Args:
            transcription_results: List of transcription results
            
        Returns:
            Merged transcription result
        """
        if not transcription_results:
            return {"text": "", "word_count": 0}
        
        if len(transcription_results) == 1:
            return transcription_results[0]
        
        # Merge text from all results
        merged_text = " ".join(result.get("text", "") for result in transcription_results)
        
        # Sum word counts
        total_words = sum(result.get("word_count", 0) for result in transcription_results)
        
        # Use first result as base and update with merged data
        merged_result = transcription_results[0].copy()
        merged_result.update({
            "text": merged_text,
            "word_count": total_words,
            "chunks_processed": len(transcription_results)
        })
        
        return merged_result
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files.
        
        Args:
            file_paths: List of file paths to clean up
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {e}")