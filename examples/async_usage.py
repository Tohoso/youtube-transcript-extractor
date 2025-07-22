#!/usr/bin/env python3
"""
Async usage examples for YouTube Transcript Extractor
"""

import sys
import os
import asyncio
import time

# パッケージのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_transcript_extractor import AsyncYouTubeTranscriptExtractor


async def basic_async_example():
    """基本的な非同期使用例"""
    print("=== 基本的な非同期使用例 ===")
    
    async with AsyncYouTubeTranscriptExtractor() as extractor:
        video_id = "dQw4w9WgXcQ"
        
        print(f"動画ID: {video_id}")
        print("非同期で文字起こしを取得中...")
        
        start_time = time.time()
        result = await extractor.get_transcript_async(video_id)
        end_time = time.time()
        
        if result.success:
            print(f"✅ 取得成功!")
            print(f"使用手法: {result.method.value}")
            print(f"処理時間: {end_time - start_time:.2f}秒")
            print(f"エントリ数: {len(result.entries)}")
        else:
            print(f"❌ 取得失敗: {result.error_message}")


async def parallel_processing_example():
    """並行処理の例"""
    print("\n=== 並行処理の例 ===")
    
    video_ids = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "kJQP7kiw5Fk",  # Luis Fonsi - Despacito
        "YQHsXMglC9A",  # Adele - Hello
        "JGwWNGJdvx8",  # Ed Sheeran - Shape of You
    ]
    
    print(f"並行処理対象: {len(video_ids)}動画")
    
    async with AsyncYouTubeTranscriptExtractor(max_workers=3) as extractor:
        start_time = time.time()
        
        # 並行処理で全動画を処理
        results = await extractor.get_multiple_transcripts(video_ids)
        
        end_time = time.time()
        
        print(f"並行処理完了: {end_time - start_time:.2f}秒")
        
        # 結果を表示
        successful = 0
        for video_id, result in zip(video_ids, results):
            if hasattr(result, 'success') and result.success:
                print(f"✅ {video_id}: {len(result.entries)}エントリ ({result.method.value})")
                successful += 1
            else:
                error_msg = str(result) if isinstance(result, Exception) else result.error_message
                print(f"❌ {video_id}: {error_msg}")
        
        print(f"\n成功率: {successful}/{len(video_ids)} ({successful/len(video_ids)*100:.1f}%)")


async def progress_callback_example():
    """進捗コールバック付き処理の例"""
    print("\n=== 進捗コールバック付き処理の例 ===")
    
    def progress_callback(current: int, total: int, video_id: str, success: bool):
        """進捗表示コールバック"""
        status = "✅" if success else "❌"
        percentage = (current / total) * 100
        print(f"{status} [{current:2d}/{total}] ({percentage:5.1f}%) {video_id}")
    
    video_ids = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "kJQP7kiw5Fk",  # Luis Fonsi - Despacito
    ]
    
    async with AsyncYouTubeTranscriptExtractor() as extractor:
        print(f"進捗表示付きで{len(video_ids)}動画を処理:")
        
        results = await extractor.get_transcripts_with_progress(
            video_ids,
            progress_callback=progress_callback
        )
        
        print(f"\n処理完了: {len(results)}件の結果")


async def performance_comparison():
    """同期処理と非同期処理の性能比較"""
    print("\n=== 性能比較: 同期 vs 非同期 ===")
    
    video_ids = [
        "dQw4w9WgXcQ",
        "9bZkp7q19f0", 
        "kJQP7kiw5Fk"
    ]
    
    # 同期処理の時間測定
    print("同期処理を実行中...")
    from youtube_transcript_extractor import YouTubeTranscriptExtractor
    
    sync_extractor = YouTubeTranscriptExtractor()
    sync_start = time.time()
    
    sync_results = []
    for video_id in video_ids:
        result = sync_extractor.get_transcript(video_id)
        sync_results.append(result)
    
    sync_end = time.time()
    sync_time = sync_end - sync_start
    
    # 非同期処理の時間測定
    print("非同期処理を実行中...")
    
    async with AsyncYouTubeTranscriptExtractor() as async_extractor:
        async_start = time.time()
        async_results = await async_extractor.get_multiple_transcripts(video_ids)
        async_end = time.time()
        async_time = async_end - async_start
    
    # 結果比較
    print(f"\n=== 性能比較結果 ===")
    print(f"同期処理時間:   {sync_time:.2f}秒")
    print(f"非同期処理時間: {async_time:.2f}秒")
    print(f"速度向上:       {sync_time/async_time:.2f}倍")
    
    # 成功率比較
    sync_success = sum(1 for r in sync_results if r.success)
    async_success = sum(1 for r in async_results if hasattr(r, 'success') and r.success)
    
    print(f"同期成功率:     {sync_success}/{len(video_ids)} ({sync_success/len(video_ids)*100:.1f}%)")
    print(f"非同期成功率:   {async_success}/{len(video_ids)} ({async_success/len(video_ids)*100:.1f}%)")


async def channel_processing_simulation():
    """チャンネル全動画処理のシミュレーション"""
    print("\n=== チャンネル全動画処理シミュレーション ===")
    
    # 仮想的なチャンネルの動画リスト（実際にはYouTube APIで取得）
    channel_videos = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "kJQP7kiw5Fk",  # Luis Fonsi - Despacito
        "YQHsXMglC9A",  # Adele - Hello
        "JGwWNGJdvx8",  # Ed Sheeran - Shape of You
    ]
    
    def channel_progress(current: int, total: int, video_id: str, success: bool):
        """チャンネル処理用進捗コールバック"""
        status = "✅" if success else "❌"
        bar_length = 20
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        percentage = (current / total) * 100
        
        print(f"\r{status} |{bar}| {current}/{total} ({percentage:5.1f}%) {video_id[:11]}", end="")
        
        if current == total:
            print()  # 最後に改行
    
    print(f"チャンネル動画数: {len(channel_videos)}")
    print("全動画の文字起こしを取得中...")
    
    async with AsyncYouTubeTranscriptExtractor(max_workers=3) as extractor:
        start_time = time.time()
        
        results = await extractor.get_transcripts_with_progress(
            channel_videos,
            progress_callback=channel_progress
        )
        
        end_time = time.time()
        
        # 結果分析
        successful_results = [r for r in results if r.success]
        total_entries = sum(len(r.entries) for r in successful_results)
        total_text_length = sum(len(r.to_plain_text()) for r in successful_results)
        
        print(f"\n=== チャンネル分析結果 ===")
        print(f"処理時間:       {end_time - start_time:.2f}秒")
        print(f"成功動画数:     {len(successful_results)}/{len(channel_videos)}")
        print(f"総エントリ数:   {total_entries:,}")
        print(f"総文字数:       {total_text_length:,}")
        print(f"平均文字数/動画: {total_text_length//len(successful_results) if successful_results else 0:,}")


async def main():
    """メイン関数"""
    print("YouTube Transcript Extractor - 非同期使用例")
    print("=" * 60)
    
    try:
        await basic_async_example()
        await parallel_processing_example()
        await progress_callback_example()
        await performance_comparison()
        await channel_processing_simulation()
        
    except KeyboardInterrupt:
        print("\n\n処理が中断されました")
    except Exception as e:
        print(f"\n\n予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n非同期処理例の実行完了")


if __name__ == "__main__":
    asyncio.run(main())

