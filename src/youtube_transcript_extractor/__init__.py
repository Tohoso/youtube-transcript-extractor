"""
YouTube Transcript Extractor

YouTube動画から文字起こしを確実に取得するPythonライブラリ
"""

__version__ = "1.0.0"
__author__ = "YouTube Transcript Extractor Team"
__email__ = "contact@example.com"
__license__ = "MIT"

from .core import (
    YouTubeTranscriptExtractor,
    TranscriptResult,
    TranscriptEntry,
    TranscriptMethod,
    TranscriptConfig,
)

from .extractors import (
    YouTubeTranscriptAPIExtractor,
    InnerTubeAPIExtractor,
    OpenAIWhisperExtractor,
    DeepgramExtractor,
    AssemblyAIExtractor,
)

from .async_extractor import AsyncYouTubeTranscriptExtractor

from .cache import TranscriptCache

from .exceptions import (
    TranscriptError,
    NoTranscriptAvailableError,
    APIQuotaExceededError,
    VideoNotFoundError,
)

__all__ = [
    # Core classes
    "YouTubeTranscriptExtractor",
    "TranscriptResult",
    "TranscriptEntry",
    "TranscriptMethod",
    "TranscriptConfig",
    
    # Extractors
    "YouTubeTranscriptAPIExtractor",
    "InnerTubeAPIExtractor", 
    "OpenAIWhisperExtractor",
    "DeepgramExtractor",
    "AssemblyAIExtractor",
    
    # Async support
    "AsyncYouTubeTranscriptExtractor",
    
    # Cache
    "TranscriptCache",
    
    # Exceptions
    "TranscriptError",
    "NoTranscriptAvailableError",
    "APIQuotaExceededError",
    "VideoNotFoundError",
]

