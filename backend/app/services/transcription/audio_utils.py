"""
Audio Utilities
Handles audio file processing, compression, and chunking for transcription
"""

import os
import tempfile
from typing import List, Tuple, Optional
from pathlib import Path
import subprocess
import wave
import math
from pydub import AudioSegment
from pydub.utils import mediainfo
from loguru import logger

from app.core.config import settings


class AudioProcessor:
    """Utilities for processing audio files before transcription."""
    
    def __init__(self):
        """Initialize audio processor with configuration."""
        self.max_file_size_mb = settings.MAX_AUDIO_FILE_SIZE_MB
        self.max_chunk_duration_seconds = settings.AUDIO_CHUNK_DURATION_SECONDS
        self.supported_formats = {'.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpga', '.webm', '.ogg'}
        
    def get_audio_info(self, file_path: str) -> dict:
        """
        Get audio file information.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio info (duration, bitrate, format, size)
        """
        try:
            info = mediainfo(file_path)
            return {
                "duration": float(info.get('duration', 0)),
                "bitrate": int(info.get('bit_rate', 0)),
                "format": info.get('format_name', ''),
                "size_bytes": os.path.getsize(file_path),
                "size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "sample_rate": int(info.get('sample_rate', 0)),
                "channels": int(info.get('channels', 0))
            }
        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            raise
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if file is supported for transcription.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if file is valid
            
        Raises:
            ValueError: If file is invalid
        """
        # Check file exists
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported: {', '.join(self.supported_formats)}")
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            logger.warning(f"File size {file_size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB")
            return False  # Will need compression or chunking
        
        return True
    
    async def compress_audio(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        target_bitrate: str = "64k"
    ) -> str:
        """
        Compress audio file to reduce size.
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path (defaults to temp file)
            target_bitrate: Target bitrate (e.g., "64k", "128k")
            
        Returns:
            Path to compressed file
        """
        try:
            # Use temp file if no output path specified
            if not output_path:
                output_path = tempfile.mktemp(suffix=".mp3")
            
            logger.info(f"Compressing audio: {input_path} -> {output_path}")
            
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Export with compression
            audio.export(
                output_path,
                format="mp3",
                bitrate=target_bitrate,
                parameters=["-ac", "1"]  # Convert to mono
            )
            
            # Check new size
            original_size = os.path.getsize(input_path) / (1024 * 1024)
            new_size = os.path.getsize(output_path) / (1024 * 1024)
            compression_ratio = (1 - new_size / original_size) * 100
            
            logger.info(f"Compression complete: {original_size:.2f}MB -> {new_size:.2f}MB ({compression_ratio:.1f}% reduction)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio compression failed: {str(e)}")
            raise
    
    async def split_audio_into_chunks(
        self,
        input_path: str,
        chunk_duration_seconds: Optional[int] = None,
        overlap_seconds: int = 5
    ) -> List[str]:
        """
        Split audio file into chunks for processing.
        
        Args:
            input_path: Path to input audio file
            chunk_duration_seconds: Duration of each chunk (defaults to max chunk duration)
            overlap_seconds: Overlap between chunks to maintain context
            
        Returns:
            List of paths to chunk files
        """
        try:
            if chunk_duration_seconds is None:
                chunk_duration_seconds = self.max_chunk_duration_seconds
            
            # Load audio
            logger.info(f"Loading audio for chunking: {input_path}")
            audio = AudioSegment.from_file(input_path)
            
            # Calculate chunk parameters
            total_duration = len(audio) / 1000  # Convert to seconds
            chunk_duration_ms = chunk_duration_seconds * 1000
            overlap_ms = overlap_seconds * 1000
            
            # Create chunks
            chunks = []
            chunk_paths = []
            start = 0
            chunk_index = 0
            
            while start < len(audio):
                # Calculate end position with overlap
                end = min(start + chunk_duration_ms, len(audio))
                
                # Extract chunk
                chunk = audio[start:end]
                
                # Save chunk to temp file
                chunk_path = tempfile.mktemp(suffix=f"_chunk_{chunk_index:03d}.mp3")
                chunk.export(chunk_path, format="mp3")
                chunk_paths.append(chunk_path)
                
                # Log chunk info
                chunk_duration = (end - start) / 1000
                logger.info(f"Created chunk {chunk_index}: {chunk_duration:.1f}s")
                
                # Move to next chunk (with overlap if not last chunk)
                if end < len(audio):
                    start = end - overlap_ms
                else:
                    start = end
                
                chunk_index += 1
            
            logger.info(f"Split audio into {len(chunk_paths)} chunks")
            return chunk_paths
            
        except Exception as e:
            logger.error(f"Audio chunking failed: {str(e)}")
            raise
    
    async def merge_transcriptions(
        self,
        transcription_chunks: List[dict],
        overlap_seconds: int = 5
    ) -> dict:
        """
        Merge transcription chunks into a single result.
        
        Args:
            transcription_chunks: List of transcription results from chunks
            overlap_seconds: Overlap that was used during chunking
            
        Returns:
            Merged transcription result
        """
        try:
            if not transcription_chunks:
                raise ValueError("No transcription chunks to merge")
            
            # If only one chunk, return it
            if len(transcription_chunks) == 1:
                return transcription_chunks[0]
            
            # Merge text
            merged_text = []
            merged_segments = []
            total_duration = 0
            
            for i, chunk in enumerate(transcription_chunks):
                text = chunk.get("text", "")
                
                # For overlapping chunks, try to detect and remove duplicate content
                if i > 0 and overlap_seconds > 0:
                    # Simple deduplication: remove last few words from previous chunk
                    # if they appear at start of current chunk
                    # This is a simplified approach - production would need better logic
                    words = text.split()
                    if len(words) > 10:
                        # Check if first words match last words of previous text
                        prev_words = merged_text[-1].split()[-10:] if merged_text else []
                        if prev_words and words[:5] == prev_words[-5:]:
                            # Skip the overlapping part
                            text = " ".join(words[5:])
                
                merged_text.append(text)
                
                # Merge segments if available
                if "segments" in chunk:
                    for segment in chunk["segments"]:
                        # Adjust timestamp offsets for subsequent chunks
                        if i > 0:
                            segment["start"] += total_duration
                            segment["end"] += total_duration
                        merged_segments.append(segment)
                
                # Update total duration
                if "duration" in chunk:
                    total_duration += chunk["duration"]
            
            # Create merged result
            result = {
                "text": " ".join(merged_text),
                "provider": transcription_chunks[0].get("provider", "groq"),
                "model": transcription_chunks[0].get("model"),
                "language": transcription_chunks[0].get("language"),
                "duration": total_duration,
                "chunks_processed": len(transcription_chunks)
            }
            
            if merged_segments:
                result["segments"] = merged_segments
            
            # Calculate word count
            result["word_count"] = len(result["text"].split())
            
            logger.info(f"Merged {len(transcription_chunks)} chunks into {result['word_count']} words")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to merge transcriptions: {str(e)}")
            raise
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files.
        
        Args:
            file_paths: List of file paths to delete
        """
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
                    logger.debug(f"Cleaned up temp file: {path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {path}: {str(e)}")
    
    async def prepare_file_for_transcription(self, input_path: str) -> Tuple[List[str], bool]:
        """
        Prepare audio file for transcription, handling size limits.
        
        Args:
            input_path: Path to input audio file
            
        Returns:
            Tuple of (list of file paths ready for transcription, needs_merging flag)
        """
        try:
            # Get file info
            info = self.get_audio_info(input_path)
            
            # If file is within size limit, return as-is
            if info["size_mb"] <= self.max_file_size_mb:
                logger.info(f"File size OK: {info['size_mb']:.2f}MB")
                return [input_path], False
            
            logger.info(f"File too large: {info['size_mb']:.2f}MB. Processing required.")
            
            # Try compression first
            if info["bitrate"] > 64000:  # If bitrate > 64kbps
                compressed_path = await self.compress_audio(input_path)
                compressed_info = self.get_audio_info(compressed_path)
                
                if compressed_info["size_mb"] <= self.max_file_size_mb:
                    logger.info("Compression successful, file now within limits")
                    return [compressed_path], False
                
                # If still too large, need to chunk
                logger.info("Compression insufficient, chunking required")
                chunks = await self.split_audio_into_chunks(compressed_path)
                
                # Clean up compressed file
                os.unlink(compressed_path)
                
                return chunks, True
            
            # If already low bitrate, go straight to chunking
            logger.info("Low bitrate file, proceeding with chunking")
            chunks = await self.split_audio_into_chunks(input_path)
            return chunks, True
            
        except Exception as e:
            logger.error(f"Failed to prepare file for transcription: {str(e)}")
            raise
