"""
Core classes and functions for YouTube transcript extraction
"""

import os
import re
import time
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptMethod(Enum):
    """文字起こし取得手法の列挙"""
    YOUTUBE_TRANSCRIPT_API = "youtube_transcript_api"
    INNERTUBE_API = "innertube_api"
    OPENAI_WHISPER = "openai_whisper"
    DEEPGRAM = "deepgram"
    ASSEMBLY_AI = "assembly_ai"


@dataclass
class TranscriptEntry:
    """文字起こしエントリ"""
    text: str
    start_time: float
    end_time: float
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


@dataclass
class TranscriptResult:
    """文字起こし結果"""
    entries: List[TranscriptEntry]
    method: TranscriptMethod
    language: str
    success: bool
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    
    def to_plain_text(self) -> str:
        """プレーンテキストに変換"""
        return " ".join([entry.text for entry in self.entries])
    
    def to_srt(self) -> str:
        """SRT形式に変換"""
        srt_content = []
        for i, entry in enumerate(self.entries, 1):
            start_time = self._format_srt_time(entry.start_time)
            end_time = self._format_srt_time(entry.end_time)
            srt_content.append(f"{i}\n{start_time} --> {end_time}\n{entry.text}\n")
        return "\n".join(srt_content)
    
    def _format_srt_time(self, seconds: float) -> str:
        """秒数をSRT時間フォーマットに変換"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


@dataclass
class TranscriptConfig:
    """文字起こし抽出器の設定"""
    # 基本設定
    preferred_language: str = "en"
    fallback_languages: List[str] = None
    fallback_methods: List[TranscriptMethod] = None
    
    # API設定
    openai_api_key: Optional[str] = None
    deepgram_api_key: Optional[str] = None
    assembly_ai_api_key: Optional[str] = None
    
    # キャッシュ設定
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    cache_dir: str = ".transcript_cache"
    
    # ログ設定
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # パフォーマンス設定
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    
    def __post_init__(self):
        if self.fallback_languages is None:
            self.fallback_languages = ["en", "auto"]
        
        if self.fallback_methods is None:
            self.fallback_methods = [
                TranscriptMethod.INNERTUBE_API,
                TranscriptMethod.YOUTUBE_TRANSCRIPT_API
            ]
        
        # 環境変数からAPIキーを取得
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.deepgram_api_key:
            self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.assembly_ai_api_key:
            self.assembly_ai_api_key = os.getenv("ASSEMBLY_AI_API_KEY")


class YouTubeTranscriptExtractor:
    """YouTube文字起こし統合抽出器"""
    
    def __init__(self, config: Optional[Union[Dict, TranscriptConfig]] = None):
        """
        初期化
        
        Args:
            config: 設定辞書またはTranscriptConfigオブジェクト
        """
        if isinstance(config, dict):
            self.config = TranscriptConfig(**config)
        elif isinstance(config, TranscriptConfig):
            self.config = config
        else:
            self.config = TranscriptConfig()
        
        # ログ設定
        self._setup_logging()
        
        # 抽出器を初期化
        self.extractors = self._initialize_extractors()
    
    def _setup_logging(self):
        """ログ設定のセットアップ"""
        log_level = getattr(logging, self.config.log_level.upper())
        logger.setLevel(log_level)
        
        if self.config.log_file:
            handler = logging.FileHandler(self.config.log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    def _initialize_extractors(self) -> Dict[TranscriptMethod, object]:
        """抽出器を初期化"""
        from .extractors import (
            YouTubeTranscriptAPIExtractor,
            InnerTubeAPIExtractor,
            OpenAIWhisperExtractor,
            DeepgramExtractor,
            AssemblyAIExtractor,
        )
        
        extractors = {}
        
        for method in self.config.fallback_methods:
            if method == TranscriptMethod.YOUTUBE_TRANSCRIPT_API:
                extractors[method] = YouTubeTranscriptAPIExtractor(self.config)
            elif method == TranscriptMethod.INNERTUBE_API:
                extractors[method] = InnerTubeAPIExtractor(self.config)
            elif method == TranscriptMethod.OPENAI_WHISPER:
                extractors[method] = OpenAIWhisperExtractor(self.config)
            elif method == TranscriptMethod.DEEPGRAM:
                extractors[method] = DeepgramExtractor(self.config)
            elif method == TranscriptMethod.ASSEMBLY_AI:
                extractors[method] = AssemblyAIExtractor(self.config)
        
        return extractors
    
    def extract_video_id(self, url_or_id: str) -> str:
        """YouTube URLまたはIDから動画IDを抽出"""
        if len(url_or_id) == 11 and "/" not in url_or_id:
            return url_or_id
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        raise ValueError(f"Invalid YouTube URL or ID: {url_or_id}")
    
    def get_transcript(self, video_url_or_id: str, language: Optional[str] = None) -> TranscriptResult:
        """
        文字起こしを取得（フォールバック機能付き）
        
        Args:
            video_url_or_id: YouTube URL または動画ID
            language: 言語コード（省略時は設定値を使用）
        
        Returns:
            TranscriptResult: 文字起こし結果
        """
        video_id = self.extract_video_id(video_url_or_id)
        target_language = language or self.config.preferred_language
        
        logger.info(f"Extracting transcript for video: {video_id}, language: {target_language}")
        
        # フォールバック手法を順次試行
        for method in self.config.fallback_methods:
            try:
                logger.info(f"Trying method: {method.value}")
                start_time = time.time()
                
                extractor = self.extractors.get(method)
                if not extractor:
                    logger.warning(f"Extractor not available for method: {method.value}")
                    continue
                
                result = extractor.extract(video_id, target_language)
                processing_time = time.time() - start_time
                result.processing_time = processing_time
                
                if result.success:
                    logger.info(f"Successfully extracted transcript using {method.value} in {processing_time:.2f}s")
                    return result
                else:
                    logger.warning(f"Method {method.value} failed: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Method {method.value} raised exception: {str(e)}")
                continue
        
        # すべての手法が失敗した場合
        return TranscriptResult(
            entries=[],
            method=self.config.fallback_methods[0] if self.config.fallback_methods else TranscriptMethod.INNERTUBE_API,
            language=target_language,
            success=False,
            error_message="All extraction methods failed"
        )

