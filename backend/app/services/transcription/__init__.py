"""Transcription service module."""

from app.services.transcription.manager import (
    TranscriptionManager,
    TranscriptionProvider,
    TranscriptionStatus
)
from app.services.transcription.groq_service import GroqTranscriptionService

# Import AudioProcessor with fallback for Python 3.13+
try:
    from app.services.transcription.audio_utils import AudioProcessor
except (ImportError, ModuleNotFoundError):
    # Fallback for Python 3.13+ or missing pydub
    try:
        from app.services.transcription.audio_utils_minimal import AudioProcessor
    except ImportError:
        from app.services.transcription.audio_utils_stub import AudioProcessor

__all__ = [
    "TranscriptionManager",
    "TranscriptionProvider",
    "TranscriptionStatus",
    "GroqTranscriptionService",
    "AudioProcessor"
]
