#!/usr/bin/env python3
"""
Tests for core functionality
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# パッケージのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from youtube_transcript_extractor import (
    YouTubeTranscriptExtractor,
    TranscriptResult,
    TranscriptEntry,
    TranscriptMethod,
    TranscriptConfig
)


class TestTranscriptEntry(unittest.TestCase):
    """TranscriptEntryクラスのテスト"""
    
    def test_transcript_entry_creation(self):
        """TranscriptEntryの作成テスト"""
        entry = TranscriptEntry(
            text="Hello world",
            start_time=10.5,
            end_time=15.2
        )
        
        self.assertEqual(entry.text, "Hello world")
        self.assertEqual(entry.start_time, 10.5)
        self.assertEqual(entry.end_time, 15.2)
    
    def test_to_dict(self):
        """to_dictメソッドのテスト"""
        entry = TranscriptEntry(
            text="Test text",
            start_time=5.0,
            end_time=10.0
        )
        
        expected = {
            "text": "Test text",
            "start_time": 5.0,
            "end_time": 10.0
        }
        
        self.assertEqual(entry.to_dict(), expected)


class TestTranscriptResult(unittest.TestCase):
    """TranscriptResultクラスのテスト"""
    
    def setUp(self):
        """テスト用データの準備"""
        self.entries = [
            TranscriptEntry("Hello", 0.0, 2.0),
            TranscriptEntry("world", 2.0, 4.0),
            TranscriptEntry("test", 4.0, 6.0)
        ]
        
        self.result = TranscriptResult(
            entries=self.entries,
            method=TranscriptMethod.INNERTUBE_API,
            language="en",
            success=True
        )
    
    def test_to_plain_text(self):
        """to_plain_textメソッドのテスト"""
        expected = "Hello world test"
        self.assertEqual(self.result.to_plain_text(), expected)
    
    def test_to_srt(self):
        """to_srtメソッドのテスト"""
        srt_content = self.result.to_srt()
        
        # SRT形式の基本構造をチェック
        self.assertIn("1\n00:00:00,000 --> 00:00:02,000\nHello", srt_content)
        self.assertIn("2\n00:00:02,000 --> 00:00:04,000\nworld", srt_content)
        self.assertIn("3\n00:00:04,000 --> 00:00:06,000\ntest", srt_content)
    
    def test_format_srt_time(self):
        """SRT時間フォーマットのテスト"""
        # プライベートメソッドのテスト
        formatted = self.result._format_srt_time(3661.5)  # 1時間1分1.5秒
        self.assertEqual(formatted, "01:01:01,500")
        
        formatted = self.result._format_srt_time(0.123)
        self.assertEqual(formatted, "00:00:00,123")


class TestTranscriptConfig(unittest.TestCase):
    """TranscriptConfigクラスのテスト"""
    
    def test_default_config(self):
        """デフォルト設定のテスト"""
        config = TranscriptConfig()
        
        self.assertEqual(config.preferred_language, "en")
        self.assertEqual(config.fallback_languages, ["en", "auto"])
        self.assertTrue(config.enable_cache)
        self.assertEqual(config.cache_ttl_hours, 24)
    
    def test_custom_config(self):
        """カスタム設定のテスト"""
        config = TranscriptConfig(
            preferred_language="ja",
            enable_cache=False,
            cache_ttl_hours=48
        )
        
        self.assertEqual(config.preferred_language, "ja")
        self.assertFalse(config.enable_cache)
        self.assertEqual(config.cache_ttl_hours, 48)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_api_key_from_env(self):
        """環境変数からのAPIキー取得テスト"""
        config = TranscriptConfig()
        self.assertEqual(config.openai_api_key, 'test_key')


class TestYouTubeTranscriptExtractor(unittest.TestCase):
    """YouTubeTranscriptExtractorクラスのテスト"""
    
    def setUp(self):
        """テスト用の抽出器を準備"""
        self.extractor = YouTubeTranscriptExtractor()
    
    def test_extract_video_id_from_id(self):
        """動画IDからの抽出テスト"""
        video_id = "dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(video_id)
        self.assertEqual(result, video_id)
    
    def test_extract_video_id_from_url(self):
        """URLからの動画ID抽出テスト"""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = self.extractor.extract_video_id(url)
                self.assertEqual(result, expected_id)
    
    def test_extract_video_id_invalid(self):
        """無効なURLでのエラーテスト"""
        invalid_urls = [
            "https://example.com/video",
            "not_a_url",
            "https://vimeo.com/123456",
            ""
        ]
        
        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url):
                with self.assertRaises(ValueError):
                    self.extractor.extract_video_id(invalid_url)
    
    def test_config_dict_initialization(self):
        """辞書設定での初期化テスト"""
        config_dict = {
            "preferred_language": "ja",
            "enable_cache": False
        }
        
        extractor = YouTubeTranscriptExtractor(config_dict)
        self.assertEqual(extractor.config.preferred_language, "ja")
        self.assertFalse(extractor.config.enable_cache)
    
    def test_config_object_initialization(self):
        """TranscriptConfigオブジェクトでの初期化テスト"""
        config = TranscriptConfig(preferred_language="fr")
        extractor = YouTubeTranscriptExtractor(config)
        self.assertEqual(extractor.config.preferred_language, "fr")


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        """統合テスト用の設定"""
        # テスト用の軽量設定
        config = TranscriptConfig(
            fallback_methods=[TranscriptMethod.INNERTUBE_API],
            enable_cache=False
        )
        self.extractor = YouTubeTranscriptExtractor(config)
    
    @unittest.skipIf(
        os.getenv('SKIP_INTEGRATION_TESTS') == '1',
        "Integration tests skipped"
    )
    def test_real_video_extraction(self):
        """実際の動画での統合テスト"""
        # 既知の字幕付き動画でテスト
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        result = self.extractor.get_transcript(video_id)
        
        # 基本的な成功条件をチェック
        if result.success:
            self.assertIsInstance(result.entries, list)
            self.assertGreater(len(result.entries), 0)
            self.assertIsInstance(result.method, TranscriptMethod)
            self.assertIsInstance(result.language, str)
            self.assertIsNotNone(result.processing_time)
            
            # エントリの構造をチェック
            for entry in result.entries[:3]:  # 最初の3エントリのみチェック
                self.assertIsInstance(entry.text, str)
                self.assertIsInstance(entry.start_time, (int, float))
                self.assertIsInstance(entry.end_time, (int, float))
                self.assertGreaterEqual(entry.end_time, entry.start_time)
        else:
            # 失敗した場合はエラーメッセージがあることを確認
            self.assertIsNotNone(result.error_message)
            self.assertIsInstance(result.error_message, str)
    
    def test_invalid_video_handling(self):
        """無効な動画IDの処理テスト"""
        invalid_id = "invalid_video_id_12345"
        
        result = self.extractor.get_transcript(invalid_id)
        
        # 失敗することを期待
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertEqual(len(result.entries), 0)


if __name__ == '__main__':
    # テスト実行時の設定
    unittest.main(verbosity=2)

