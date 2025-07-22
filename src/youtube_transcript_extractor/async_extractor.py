"""
Async support for YouTube transcript extraction
"""

import asyncio
import time
from typing import List, Optional, Union
from concurrent.futures import ThreadPoolExecutor

from .core import YouTubeTranscriptExtractor, TranscriptResult, TranscriptConfig


class AsyncYouTubeTranscriptExtractor:
    """非同期YouTube文字起こし抽出器"""
    
    def __init__(self, config: Optional[Union[dict, TranscriptConfig]] = None, max_workers: int = 5):
        """
        初期化
        
        Args:
            config: 設定辞書またはTranscriptConfigオブジェクト
            max_workers: 最大ワーカー数
        """
        self.config = config
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def get_transcript_async(self, video_url_or_id: str, language: str = "en") -> TranscriptResult:
        """
        非同期で文字起こしを取得
        
        Args:
            video_url_or_id: YouTube URL または動画ID
            language: 言語コード
        
        Returns:
            TranscriptResult: 文字起こし結果
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._get_transcript_sync, 
            video_url_or_id, 
            language
        )
    
    async def get_multiple_transcripts(
        self, 
        video_ids: List[str], 
        language: str = "en"
    ) -> List[Union[TranscriptResult, Exception]]:
        """
        複数動画の文字起こしを並行取得
        
        Args:
            video_ids: 動画IDのリスト
            language: 言語コード
        
        Returns:
            List[Union[TranscriptResult, Exception]]: 結果のリスト
        """
        tasks = [
            self.get_transcript_async(video_id, language) 
            for video_id in video_ids
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def get_transcripts_with_progress(
        self,
        video_ids: List[str],
        language: str = "en",
        progress_callback: Optional[callable] = None
    ) -> List[TranscriptResult]:
        """
        進捗コールバック付きで複数動画の文字起こしを取得
        
        Args:
            video_ids: 動画IDのリスト
            language: 言語コード
            progress_callback: 進捗コールバック関数
        
        Returns:
            List[TranscriptResult]: 結果のリスト
        """
        results = []
        total = len(video_ids)
        
        for i, video_id in enumerate(video_ids):
            try:
                result = await self.get_transcript_async(video_id, language)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total, video_id, result.success)
                    
            except Exception as e:
                error_result = TranscriptResult(
                    entries=[], 
                    method=None, 
                    language=language, 
                    success=False,
                    error_message=str(e)
                )
                results.append(error_result)
                
                if progress_callback:
                    progress_callback(i + 1, total, video_id, False)
        
        return results
    
    def _get_transcript_sync(self, video_url_or_id: str, language: str) -> TranscriptResult:
        """同期版の文字起こし取得（内部使用）"""
        extractor = YouTubeTranscriptExtractor(self.config)
        return extractor.get_transcript(video_url_or_id, language)
    
    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリ"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了"""
        self.executor.shutdown(wait=True)


# 使用例とヘルパー関数
async def extract_channel_transcripts(
    channel_videos: List[str], 
    language: str = "en",
    max_workers: int = 5,
    progress_callback: Optional[callable] = None
) -> dict:
    """
    チャンネルの全動画から文字起こしを取得
    
    Args:
        channel_videos: チャンネルの動画IDリスト
        language: 言語コード
        max_workers: 最大ワーカー数
        progress_callback: 進捗コールバック
    
    Returns:
        dict: {video_id: TranscriptResult} の辞書
    """
    async with AsyncYouTubeTranscriptExtractor(max_workers=max_workers) as extractor:
        results = await extractor.get_transcripts_with_progress(
            channel_videos, 
            language, 
            progress_callback
        )
    
    return {
        video_id: result 
        for video_id, result in zip(channel_videos, results)
    }


def simple_progress_callback(current: int, total: int, video_id: str, success: bool):
    """シンプルな進捗表示コールバック"""
    status = "✅" if success else "❌"
    print(f"{status} [{current}/{total}] {video_id}")


# 使用例
async def main():
    """使用例のメイン関数"""
    # 単一動画の非同期処理
    async with AsyncYouTubeTranscriptExtractor() as extractor:
        result = await extractor.get_transcript_async("dQw4w9WgXcQ")
        print(f"Result: {result.success}")
    
    # 複数動画の並行処理
    video_ids = ["dQw4w9WgXcQ", "9bZkp7q19f0", "kJQP7kiw5Fk"]
    results = await extract_channel_transcripts(
        video_ids, 
        progress_callback=simple_progress_callback
    )
    
    for video_id, result in results.items():
        if result.success:
            print(f"✅ {video_id}: {len(result.entries)} entries")
        else:
            print(f"❌ {video_id}: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())

