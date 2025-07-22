#!/usr/bin/env python3
"""
Basic usage examples for YouTube Transcript Extractor
"""

import sys
import os

# パッケージのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_transcript_extractor import (
    YouTubeTranscriptExtractor,
    TranscriptMethod,
    TranscriptConfig
)


def basic_example():
    """基本的な使用例"""
    print("=== 基本的な使用例 ===")
    
    # デフォルト設定で抽出器を作成
    extractor = YouTubeTranscriptExtractor()
    
    # Rick Astley - Never Gonna Give You Up
    video_id = "dQw4w9WgXcQ"
    
    print(f"動画ID: {video_id}")
    print("文字起こしを取得中...")
    
    result = extractor.get_transcript(video_id)
    
    if result.success:
        print(f"✅ 取得成功!")
        print(f"使用手法: {result.method.value}")
        print(f"言語: {result.language}")
        print(f"処理時間: {result.processing_time:.2f}秒")
        print(f"エントリ数: {len(result.entries)}")
        
        # 最初の3エントリを表示
        print("\n最初の3エントリ:")
        for i, entry in enumerate(result.entries[:3]):
            print(f"{i+1}. [{entry.start_time:.2f}s] {entry.text}")
        
        # プレーンテキスト（最初の200文字）
        plain_text = result.to_plain_text()
        print(f"\nプレーンテキスト（最初の200文字）:")
        print(f"{plain_text[:200]}...")
        
    else:
        print(f"❌ 取得失敗: {result.error_message}")


def custom_config_example():
    """カスタム設定の使用例"""
    print("\n=== カスタム設定の使用例 ===")
    
    # カスタム設定
    config = TranscriptConfig(
        preferred_language="ja",  # 日本語を優先
        fallback_methods=[
            TranscriptMethod.INNERTUBE_API,
            TranscriptMethod.YOUTUBE_TRANSCRIPT_API
        ],
        enable_cache=True,
        cache_ttl_hours=48  # 48時間キャッシュ
    )
    
    extractor = YouTubeTranscriptExtractor(config)
    
    # 日本語の動画例（適当な動画ID）
    video_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"  # PSY - GANGNAM STYLE
    
    print(f"動画URL: {video_url}")
    print("カスタム設定で文字起こしを取得中...")
    
    result = extractor.get_transcript(video_url, language="en")
    
    if result.success:
        print(f"✅ 取得成功!")
        print(f"使用手法: {result.method.value}")
        print(f"言語: {result.language}")
        print(f"エントリ数: {len(result.entries)}")
        
        # SRT形式で保存
        srt_content = result.to_srt()
        with open("example_transcript.srt", "w", encoding="utf-8") as f:
            f.write(srt_content)
        print("SRT形式でexample_transcript.srtに保存しました")
        
    else:
        print(f"❌ 取得失敗: {result.error_message}")


def multiple_videos_example():
    """複数動画の処理例"""
    print("\n=== 複数動画の処理例 ===")
    
    extractor = YouTubeTranscriptExtractor()
    
    # テスト動画のリスト
    video_ids = [
        "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "9bZkp7q19f0",  # PSY - GANGNAM STYLE
        "kJQP7kiw5Fk",  # Luis Fonsi - Despacito
    ]
    
    print(f"処理対象: {len(video_ids)}動画")
    
    results = {}
    for i, video_id in enumerate(video_ids, 1):
        print(f"\n[{i}/{len(video_ids)}] {video_id} を処理中...")
        
        result = extractor.get_transcript(video_id)
        results[video_id] = result
        
        if result.success:
            print(f"✅ 成功: {len(result.entries)}エントリ ({result.method.value})")
        else:
            print(f"❌ 失敗: {result.error_message}")
    
    # 結果サマリー
    successful = sum(1 for r in results.values() if r.success)
    print(f"\n=== 結果サマリー ===")
    print(f"成功: {successful}/{len(video_ids)} 動画")
    print(f"成功率: {successful/len(video_ids)*100:.1f}%")


def error_handling_example():
    """エラーハンドリングの例"""
    print("\n=== エラーハンドリングの例 ===")
    
    extractor = YouTubeTranscriptExtractor()
    
    # 存在しない動画ID
    invalid_video_id = "invalid_video_id"
    
    print(f"無効な動画ID: {invalid_video_id}")
    
    try:
        result = extractor.get_transcript(invalid_video_id)
        
        if result.success:
            print("✅ 予期しない成功")
        else:
            print(f"❌ 期待通りの失敗: {result.error_message}")
            
    except Exception as e:
        print(f"🚨 例外が発生: {str(e)}")
    
    # 無効なURL
    invalid_url = "https://example.com/invalid"
    
    print(f"\n無効なURL: {invalid_url}")
    
    try:
        video_id = extractor.extract_video_id(invalid_url)
        print(f"抽出された動画ID: {video_id}")
    except ValueError as e:
        print(f"❌ 期待通りのエラー: {str(e)}")


def main():
    """メイン関数"""
    print("YouTube Transcript Extractor - 使用例")
    print("=" * 50)
    
    try:
        basic_example()
        custom_config_example()
        multiple_videos_example()
        error_handling_example()
        
    except KeyboardInterrupt:
        print("\n\n処理が中断されました")
    except Exception as e:
        print(f"\n\n予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n処理完了")


if __name__ == "__main__":
    main()

