"""
Individual transcript extractors for different methods
"""

import os
import re
import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Optional
from xml.etree import ElementTree as ET

from .core import TranscriptResult, TranscriptEntry, TranscriptMethod, TranscriptConfig
from .exceptions import TranscriptError, NoTranscriptAvailableError

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """抽出器の基底クラス"""
    
    def __init__(self, config: TranscriptConfig):
        self.config = config
    
    @abstractmethod
    def extract(self, video_id: str, language: str) -> TranscriptResult:
        """文字起こしを抽出"""
        pass


class YouTubeTranscriptAPIExtractor(BaseExtractor):
    """youtube-transcript-apiを使用した抽出器"""
    
    def extract(self, video_id: str, language: str) -> TranscriptResult:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
        except ImportError:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.YOUTUBE_TRANSCRIPT_API,
                language=language, success=False,
                error_message="youtube-transcript-api not installed"
            )
        
        try:
            # 利用可能な言語を取得
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 指定言語を試行
            try:
                transcript = transcript_list.find_transcript([language])
            except NoTranscriptFound:
                # 英語にフォールバック
                if language != "en":
                    transcript = transcript_list.find_transcript(["en"])
                else:
                    raise
            
            # 文字起こしデータを取得
            transcript_data = transcript.fetch()
            
            entries = []
            for item in transcript_data:
                entries.append(TranscriptEntry(
                    text=item["text"],
                    start_time=item["start"],
                    end_time=item["start"] + item["duration"]
                ))
            
            return TranscriptResult(
                entries=entries,
                method=TranscriptMethod.YOUTUBE_TRANSCRIPT_API,
                language=transcript.language_code,
                success=True
            )
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.YOUTUBE_TRANSCRIPT_API,
                language=language, success=False,
                error_message=str(e)
            )
        except Exception as e:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.YOUTUBE_TRANSCRIPT_API,
                language=language, success=False,
                error_message=f"Unexpected error: {str(e)}"
            )


class InnerTubeAPIExtractor(BaseExtractor):
    """InnerTube APIを使用した抽出器"""
    
    def extract(self, video_id: str, language: str) -> TranscriptResult:
        try:
            # 動画ページからAPIキーを取得
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(video_url, headers=headers, timeout=self.config.request_timeout)
            response.raise_for_status()
            html = response.text
            
            # APIキーを抽出
            api_key_patterns = [
                r'"INNERTUBE_API_KEY":"([^"]+)"',
                r'"innertubeApiKey":"([^"]+)"',
                r'INNERTUBE_API_KEY["\s]*:["\s]*([^"]+)',
            ]
            
            api_key = None
            for pattern in api_key_patterns:
                match = re.search(pattern, html)
                if match:
                    api_key = match.group(1)
                    break
            
            if not api_key:
                raise Exception("INNERTUBE_API_KEY not found in video page")
            
            # InnerTube player APIを呼び出し
            player_url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
            player_data = {
                "context": {
                    "client": {
                        "clientName": "ANDROID",
                        "clientVersion": "20.10.38"
                    }
                },
                "videoId": video_id
            }
            
            response = requests.post(
                player_url, 
                json=player_data, 
                headers=headers,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            player_response = response.json()
            
            # キャプショントラックを取得
            captions = player_response.get("captions", {})
            tracks = captions.get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
            
            if not tracks:
                raise Exception("No caption tracks found")
            
            # 指定言語のトラックを検索
            target_track = None
            for track in tracks:
                if track.get("languageCode") == language:
                    target_track = track
                    break
            
            # 英語にフォールバック
            if not target_track and language != "en":
                for track in tracks:
                    if track.get("languageCode") == "en":
                        target_track = track
                        break
            
            # 最初のトラックを使用
            if not target_track:
                target_track = tracks[0]
            
            # キャプションXMLを取得
            base_url = target_track["baseUrl"].replace("&fmt=srv3", "")
            xml_response = requests.get(base_url, timeout=self.config.request_timeout)
            xml_response.raise_for_status()
            xml_content = xml_response.text
            
            # XMLを解析
            root = ET.fromstring(xml_content)
            entries = []
            
            for text_elem in root.findall("text"):
                start = float(text_elem.get("start", 0))
                duration = float(text_elem.get("dur", 0))
                text = text_elem.text or ""
                
                # HTMLエンティティをデコード
                import html
                text = html.unescape(text)
                
                entries.append(TranscriptEntry(
                    text=text,
                    start_time=start,
                    end_time=start + duration
                ))
            
            return TranscriptResult(
                entries=entries,
                method=TranscriptMethod.INNERTUBE_API,
                language=target_track.get("languageCode", language),
                success=True
            )
            
        except requests.exceptions.RequestException as e:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.INNERTUBE_API,
                language=language, success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.INNERTUBE_API,
                language=language, success=False,
                error_message=f"InnerTube API error: {str(e)}"
            )


class OpenAIWhisperExtractor(BaseExtractor):
    """OpenAI Whisper APIを使用した抽出器"""
    
    def extract(self, video_id: str, language: str) -> TranscriptResult:
        if not self.config.openai_api_key:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.OPENAI_WHISPER,
                language=language, success=False,
                error_message="OpenAI API key not provided"
            )
        
        try:
            import openai
        except ImportError:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.OPENAI_WHISPER,
                language=language, success=False,
                error_message="openai package not installed"
            )
        
        try:
            # 音声ファイルをダウンロード
            audio_file_path = self._download_audio(video_id)
            
            # Whisper APIで文字起こし
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            with open(audio_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            # 結果を変換
            entries = []
            if hasattr(transcript, 'segments') and transcript.segments:
                for segment in transcript.segments:
                    entries.append(TranscriptEntry(
                        text=segment.text.strip(),
                        start_time=segment.start,
                        end_time=segment.end
                    ))
            else:
                # フォールバック: 全体テキスト
                entries.append(TranscriptEntry(
                    text=transcript.text,
                    start_time=0.0,
                    end_time=0.0
                ))
            
            # 一時ファイルを削除
            if os.path.exists(audio_file_path):
                os.unlink(audio_file_path)
            
            return TranscriptResult(
                entries=entries,
                method=TranscriptMethod.OPENAI_WHISPER,
                language=transcript.language if hasattr(transcript, 'language') else language,
                success=True
            )
            
        except Exception as e:
            return TranscriptResult(
                entries=[], method=TranscriptMethod.OPENAI_WHISPER,
                language=language, success=False,
                error_message=f"OpenAI Whisper error: {str(e)}"
            )
    
    def _download_audio(self, video_id: str) -> str:
        """音声ファイルをダウンロード"""
        try:
            import yt_dlp
            import tempfile
        except ImportError:
            raise Exception("yt-dlp package not installed")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                url = f"https://www.youtube.com/watch?v={video_id}"
                ydl.download([url])
            
            # ダウンロードされたファイルを検索
            for file in os.listdir(temp_dir):
                if file.startswith(video_id):
                    # 一時ディレクトリ外にコピー
                    import shutil
                    dest_path = f"/tmp/{file}"
                    shutil.copy2(os.path.join(temp_dir, file), dest_path)
                    return dest_path
            
            raise Exception("Downloaded audio file not found")


class DeepgramExtractor(BaseExtractor):
    """Deepgram APIを使用した抽出器（実装スケルトン）"""
    
    def extract(self, video_id: str, language: str) -> TranscriptResult:
        return TranscriptResult(
            entries=[], method=TranscriptMethod.DEEPGRAM,
            language=language, success=False,
            error_message="Deepgram implementation not completed"
        )


class AssemblyAIExtractor(BaseExtractor):
    """AssemblyAI APIを使用した抽出器（実装スケルトン）"""
    
    def extract(self, video_id: str, language: str) -> TranscriptResult:
        return TranscriptResult(
            entries=[], method=TranscriptMethod.ASSEMBLY_AI,
            language=language, success=False,
            error_message="AssemblyAI implementation not completed"
        )

