"""
Caching functionality for transcript results
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from .core import TranscriptResult, TranscriptEntry, TranscriptMethod


class TranscriptCache:
    """文字起こし結果のキャッシュ管理"""
    
    def __init__(self, cache_dir: str = ".transcript_cache", ttl_hours: int = 24):
        """
        初期化
        
        Args:
            cache_dir: キャッシュディレクトリ
            ttl_hours: キャッシュの有効期間（時間）
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, video_id: str, language: str) -> str:
        """キャッシュキーを生成"""
        key_string = f"{video_id}_{language}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """キャッシュファイルパスを取得"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, video_id: str, language: str) -> Optional[TranscriptResult]:
        """
        キャッシュから文字起こしを取得
        
        Args:
            video_id: 動画ID
            language: 言語コード
        
        Returns:
            Optional[TranscriptResult]: キャッシュされた結果（存在しない場合はNone）
        """
        cache_key = self._get_cache_key(video_id, language)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # TTL確認
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                os.remove(cache_path)
                return None
            
            # TranscriptResultを復元
            entries = [
                TranscriptEntry(
                    text=entry['text'],
                    start_time=entry['start_time'],
                    end_time=entry['end_time']
                ) 
                for entry in cache_data['entries']
            ]
            
            return TranscriptResult(
                entries=entries,
                method=TranscriptMethod(cache_data['method']),
                language=cache_data['language'],
                success=cache_data['success'],
                processing_time=cache_data.get('processing_time')
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 破損したキャッシュファイルを削除
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
        except Exception:
            return None
    
    def set(self, video_id: str, language: str, result: TranscriptResult):
        """
        文字起こし結果をキャッシュに保存
        
        Args:
            video_id: 動画ID
            language: 言語コード
            result: 文字起こし結果
        """
        if not result.success:
            return  # 失敗した結果はキャッシュしない
        
        cache_key = self._get_cache_key(video_id, language)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'video_id': video_id,
            'language': language,
            'entries': [entry.to_dict() for entry in result.entries],
            'method': result.method.value,
            'success': result.success,
            'processing_time': result.processing_time
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # キャッシュ保存失敗は無視
    
    def clear(self, video_id: Optional[str] = None, language: Optional[str] = None):
        """
        キャッシュをクリア
        
        Args:
            video_id: 特定の動画IDのキャッシュのみクリア（省略時は全て）
            language: 特定の言語のキャッシュのみクリア（省略時は全て）
        """
        if video_id and language:
            # 特定のキャッシュのみ削除
            cache_key = self._get_cache_key(video_id, language)
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            # 全キャッシュまたは条件に合うキャッシュを削除
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                cache_path = os.path.join(self.cache_dir, filename)
                
                if video_id or language:
                    # 条件指定がある場合は内容を確認
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        should_delete = True
                        if video_id and cache_data.get('video_id') != video_id:
                            should_delete = False
                        if language and cache_data.get('language') != language:
                            should_delete = False
                        
                        if should_delete:
                            os.remove(cache_path)
                    except Exception:
                        # 読み込めないファイルは削除
                        os.remove(cache_path)
                else:
                    # 全削除
                    os.remove(cache_path)
    
    def cleanup_expired(self):
        """期限切れのキャッシュを削除"""
        current_time = datetime.now()
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            cache_path = os.path.join(self.cache_dir, filename)
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if current_time - cached_time > self.ttl:
                    os.remove(cache_path)
                    
            except Exception:
                # 読み込めないファイルは削除
                os.remove(cache_path)
    
    def get_cache_info(self) -> dict:
        """キャッシュの統計情報を取得"""
        total_files = 0
        total_size = 0
        expired_files = 0
        current_time = datetime.now()
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            cache_path = os.path.join(self.cache_dir, filename)
            total_files += 1
            total_size += os.path.getsize(cache_path)
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if current_time - cached_time > self.ttl:
                    expired_files += 1
                    
            except Exception:
                expired_files += 1
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'expired_files': expired_files,
            'valid_files': total_files - expired_files,
            'cache_dir': self.cache_dir,
            'ttl_hours': self.ttl.total_seconds() / 3600
        }

