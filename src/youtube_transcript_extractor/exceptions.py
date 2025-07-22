"""
Custom exceptions for YouTube transcript extraction
"""


class TranscriptError(Exception):
    """文字起こし取得エラーの基底クラス"""
    pass


class NoTranscriptAvailableError(TranscriptError):
    """字幕が利用できない場合のエラー"""
    pass


class APIQuotaExceededError(TranscriptError):
    """API制限に達した場合のエラー"""
    pass


class VideoNotFoundError(TranscriptError):
    """動画が見つからない場合のエラー"""
    pass


class InvalidVideoURLError(TranscriptError):
    """無効な動画URLの場合のエラー"""
    pass


class AudioDownloadError(TranscriptError):
    """音声ダウンロードエラー"""
    pass


class APIKeyMissingError(TranscriptError):
    """APIキーが設定されていない場合のエラー"""
    pass

