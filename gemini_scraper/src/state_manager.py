#!/usr/bin/env python3
"""
狀態管理模組

負責管理爬蟲的執行狀態，提供：
- Session 管理 (開始、結束、統計)
- 已處理貼文 ID 追蹤 (去重)
- 狀態持久化 (斷點續傳)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class StateManager:
    """
    爬蟲狀態管理器

    使用方式:
        state = StateManager('state/scraper_state.json')
        session_id = state.start_session()
        state.mark_processed('post_123', session_id)
        if not state.is_processed('post_456'):
            # 處理貼文...
        state.end_session(session_id, 'completed')
    """

    def __init__(self, state_file='state/scraper_state.json'):
        """
        初始化狀態管理器

        Args:
            state_file (str): 狀態檔案路徑
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_or_create()
        self._processed_ids_cache = set(
            p['id'] for p in self.state['processed_post_ids']
        )

    def _load_or_create(self) -> Dict:
        """
        載入現有狀態檔或建立新的

        Returns:
            Dict: 狀態資料
        """
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'version': '1.0',
                'sessions': [],
                'processed_post_ids': [],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_all_time': 0
                }
            }

    def save(self):
        """儲存狀態到檔案"""
        self.state['metadata']['last_updated'] = datetime.now().isoformat()

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def start_session(self) -> str:
        """
        開始新的爬取 session

        Returns:
            str: Session ID (格式: YYYYMMDD_HHMMSS)
        """
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'running',  # running, completed, failed, interrupted
            'total_processed': 0,
            'total_failed': 0,
            'total_skipped': 0  # 已處理過的 (去重)
        }

        self.state['sessions'].append(session)
        self.save()

        return session_id

    def end_session(self, session_id: str, status: str = 'completed'):
        """
        結束 session

        Args:
            session_id (str): Session ID
            status (str): 結束狀態 (completed, failed, interrupted)
        """
        for session in self.state['sessions']:
            if session['session_id'] == session_id:
                session['end_time'] = datetime.now().isoformat()
                session['status'] = status
                break

        self.save()

    def is_processed(self, post_id: str) -> bool:
        """
        檢查貼文是否已處理過

        Args:
            post_id (str): 貼文 ID

        Returns:
            bool: True 表示已處理
        """
        return post_id in self._processed_ids_cache

    def mark_processed(self, post_id: str, session_id: str):
        """
        標記貼文為已處理

        Args:
            post_id (str): 貼文 ID
            session_id (str): Session ID
        """
        if not self.is_processed(post_id):
            # 添加到狀態
            self.state['processed_post_ids'].append({
                'id': post_id,
                'processed_at': datetime.now().isoformat(),
                'session_id': session_id
            })

            # 更新快取
            self._processed_ids_cache.add(post_id)

            # 更新總計
            self.state['metadata']['total_all_time'] += 1

            # 更新 session 統計
            self._update_session_stat(session_id, 'total_processed', 1)

            self.save()

    def mark_failed(self, session_id: str):
        """
        增加失敗計數

        Args:
            session_id (str): Session ID
        """
        self._update_session_stat(session_id, 'total_failed', 1)
        self.save()

    def mark_skipped(self, session_id: str):
        """
        增加跳過計數 (已處理過的貼文)

        Args:
            session_id (str): Session ID
        """
        self._update_session_stat(session_id, 'total_skipped', 1)
        self.save()

    def _update_session_stat(self, session_id: str, stat_name: str, increment: int = 1):
        """
        更新 session 統計

        Args:
            session_id (str): Session ID
            stat_name (str): 統計項目名稱
            increment (int): 增加數量
        """
        for session in self.state['sessions']:
            if session['session_id'] == session_id:
                session[stat_name] += increment
                break

    def get_stats(self) -> Dict:
        """
        取得統計資訊

        Returns:
            Dict: 包含各種統計的字典
        """
        latest_session = self.state['sessions'][-1] if self.state['sessions'] else None

        return {
            'total_all_time': self.state['metadata']['total_all_time'],
            'total_sessions': len(self.state['sessions']),
            'latest_session': latest_session
        }

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        取得特定 session 的資訊

        Args:
            session_id (str): Session ID

        Returns:
            Optional[Dict]: Session 資料，若不存在則為 None
        """
        for session in self.state['sessions']:
            if session['session_id'] == session_id:
                return session
        return None

    def cleanup_old_data(self, keep_days: int = 30):
        """
        清理舊資料 (保留最近 N 天)

        Args:
            keep_days (int): 保留天數
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cutoff_str = cutoff_date.isoformat()

        # 清理舊的 processed_post_ids
        self.state['processed_post_ids'] = [
            p for p in self.state['processed_post_ids']
            if p['processed_at'] >= cutoff_str
        ]

        # 清理舊的 sessions
        self.state['sessions'] = [
            s for s in self.state['sessions']
            if s['start_time'] >= cutoff_str
        ]

        # 重建快取
        self._processed_ids_cache = set(
            p['id'] for p in self.state['processed_post_ids']
        )

        self.save()


# 測試程式碼
if __name__ == '__main__':
    print("測試 State Manager...")

    # 建立測試用的狀態管理器
    sm = StateManager('test_state/test_state.json')

    # 測試 1: 開始 session
    print("\n[測試 1] 開始 Session")
    session_id = sm.start_session()
    print(f"✅ Session ID: {session_id}")

    # 測試 2: 標記貼文為已處理
    print("\n[測試 2] 標記貼文為已處理")
    sm.mark_processed('test_post_001', session_id)
    sm.mark_processed('test_post_002', session_id)
    sm.mark_processed('test_post_003', session_id)
    print(f"✅ 已處理 3 則貼文")

    # 測試 3: 去重檢查
    print("\n[測試 3] 去重檢查")
    assert sm.is_processed('test_post_001') == True
    print("✅ test_post_001 已處理")

    assert sm.is_processed('test_post_999') == False
    print("✅ test_post_999 未處理")

    # 測試 4: 重複標記 (應該不會增加計數)
    print("\n[測試 4] 重複標記")
    sm.mark_processed('test_post_001', session_id)  # 重複
    stats = sm.get_stats()
    assert stats['total_all_time'] == 3  # 仍然是 3
    print("✅ 重複標記不會增加計數")

    # 測試 5: 失敗和跳過計數
    print("\n[測試 5] 失敗和跳過計數")
    sm.mark_failed(session_id)
    sm.mark_skipped(session_id)
    session = sm.get_session(session_id)
    assert session['total_failed'] == 1
    assert session['total_skipped'] == 1
    print("✅ 失敗和跳過計數正確")

    # 測試 6: 結束 session
    print("\n[測試 6] 結束 Session")
    sm.end_session(session_id, 'completed')
    session = sm.get_session(session_id)
    assert session['status'] == 'completed'
    print("✅ Session 已正確結束")

    # 測試 7: 取得統計
    print("\n[測試 7] 統計資訊")
    stats = sm.get_stats()
    print(f"總處理數: {stats['total_all_time']}")
    print(f"Session 數: {stats['total_sessions']}")
    print(f"最新 Session: {stats['latest_session']['session_id']}")
    print(f"  - 成功: {stats['latest_session']['total_processed']}")
    print(f"  - 失敗: {stats['latest_session']['total_failed']}")
    print(f"  - 跳過: {stats['latest_session']['total_skipped']}")

    # 測試 8: 持久化 (重新載入)
    print("\n[測試 8] 持久化測試")
    sm2 = StateManager('test_state/test_state.json')
    assert sm2.is_processed('test_post_001') == True
    assert sm2.get_stats()['total_all_time'] == 3
    print("✅ 狀態成功持久化並重新載入")

    print("\n✅ 所有測試通過！")
    print(f"狀態檔案: test_state/test_state.json")
