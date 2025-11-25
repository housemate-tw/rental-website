#!/usr/bin/env python3
"""
資料儲存模組

負責將抓取到的貼文資料儲存到檔案，提供：
- 儲存原始貼文到 JSONL
- 檔案鎖定機制 (防止併發寫入衝突)
- 自動建立目錄
- 按日期分檔
"""

import json
import os
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Dict


class PostSaver:
    """
    貼文儲存器

    使用方式:
        saver = PostSaver(data_dir='data/', logger=logger)
        result = saver.save_post(post_data)
        print(f"已儲存: {result['filepath']}")
    """

    def __init__(self, data_dir: str, logger):
        """
        初始化儲存器

        Args:
            data_dir (str): 資料目錄路徑
            logger: ScraperLogger 物件
        """
        self.data_dir = Path(data_dir)
        self.logger = logger

        # 確保資料目錄存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"資料目錄: {self.data_dir}")

    def save_post(self, post_data: Dict) -> Dict:
        """
        儲存貼文到 JSONL 檔案

        Args:
            post_data (Dict): 貼文資料

        Returns:
            Dict: {
                'success': bool,
                'filepath': str,
                'record_id': str,
                'sequence': int
            }
        """
        try:
            # 取得今天的檔案路徑
            today = datetime.now().strftime('%Y-%m-%d')
            filepath = self.data_dir / f"{today}_raw_posts.jsonl"

            # 使用檔案鎖定機制安全寫入
            with open(filepath, 'a+', encoding='utf-8') as f:
                # 鎖定檔案
                fcntl.flock(f, fcntl.LOCK_EX)

                try:
                    # 讀取現有記錄數量
                    f.seek(0)
                    count = sum(1 for line in f if line.strip())

                    # 計算序號
                    sequence = count + 1
                    record_id = f"{today}-{sequence:03d}"

                    # 準備資料
                    data = {
                        'record_id': record_id,
                        'sequence': sequence,
                        'post_id': post_data.get('id'),
                        'text': post_data.get('text'),
                        'url': post_data.get('url'),
                        'author': post_data.get('author'),
                        'timestamp': post_data.get('timestamp'),
                        'extracted_at': post_data.get('extracted_at'),
                        'saved_at': datetime.now().isoformat()
                    }

                    # 寫入檔案
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')

                    self.logger.debug(f"✅ 已儲存: {record_id}")

                    return {
                        'success': True,
                        'filepath': str(filepath),
                        'record_id': record_id,
                        'sequence': sequence
                    }

                finally:
                    # 解鎖檔案
                    fcntl.flock(f, fcntl.LOCK_UN)

        except Exception as e:
            self.logger.error(f"儲存貼文失敗: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_stats(self) -> Dict:
        """
        取得儲存統計資訊

        Returns:
            Dict: {
                'total_files': int,
                'total_posts': int,
                'files': List[Dict]
            }
        """
        try:
            files_info = []
            total_posts = 0

            # 遍歷所有 JSONL 檔案
            for filepath in sorted(self.data_dir.glob('*_raw_posts.jsonl')):
                with open(filepath, 'r', encoding='utf-8') as f:
                    count = sum(1 for line in f if line.strip())
                    total_posts += count

                    files_info.append({
                        'filename': filepath.name,
                        'date': filepath.stem.split('_')[0],
                        'count': count,
                        'size': filepath.stat().st_size
                    })

            return {
                'total_files': len(files_info),
                'total_posts': total_posts,
                'files': files_info
            }

        except Exception as e:
            self.logger.error(f"取得統計失敗: {e}", exc_info=True)
            return {
                'total_files': 0,
                'total_posts': 0,
                'files': []
            }

    def load_posts_by_date(self, date: str = None):
        """
        載入指定日期的貼文

        Args:
            date (str, optional): 日期 (YYYY-MM-DD)，預設為今天

        Returns:
            List[Dict]: 貼文列表
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')

            filepath = self.data_dir / f"{date}_raw_posts.jsonl"

            if not filepath.exists():
                self.logger.warning(f"檔案不存在: {filepath}")
                return []

            posts = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        posts.append(json.loads(line))

            self.logger.info(f"載入 {len(posts)} 筆貼文 ({date})")
            return posts

        except Exception as e:
            self.logger.error(f"載入貼文失敗: {e}", exc_info=True)
            return []


# 測試程式碼
if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    from logger import ScraperLogger

    print("測試 PostSaver...")

    # 初始化
    logger = ScraperLogger('test_logs/')
    saver = PostSaver('test_data/', logger)

    # 測試 1: 儲存貼文
    print("\n[測試 1] 儲存貼文")
    test_post = {
        'id': 'test_12345',
        'text': '這是一則測試貼文',
        'url': 'https://facebook.com/posts/12345',
        'author': '測試作者',
        'timestamp': datetime.now().isoformat(),
        'extracted_at': datetime.now().isoformat()
    }

    result = saver.save_post(test_post)
    print(f"✅ 儲存結果: {result}")

    # 測試 2: 再儲存一則 (測試序號遞增)
    print("\n[測試 2] 儲存第二則貼文")
    test_post2 = {
        'id': 'test_67890',
        'text': '這是第二則測試貼文',
        'url': 'https://facebook.com/posts/67890',
        'author': '測試作者',
        'timestamp': datetime.now().isoformat(),
        'extracted_at': datetime.now().isoformat()
    }

    result2 = saver.save_post(test_post2)
    print(f"✅ 儲存結果: {result2}")
    print(f"序號是否遞增: {result2['sequence'] == result['sequence'] + 1}")

    # 測試 3: 取得統計
    print("\n[測試 3] 取得統計資訊")
    stats = saver.get_stats()
    print(f"✅ 統計:")
    print(f"  總檔案數: {stats['total_files']}")
    print(f"  總貼文數: {stats['total_posts']}")
    for file_info in stats['files']:
        print(f"  - {file_info['filename']}: {file_info['count']} 筆")

    # 測試 4: 載入貼文
    print("\n[測試 4] 載入貼文")
    posts = saver.load_posts_by_date()
    print(f"✅ 載入 {len(posts)} 筆貼文")
    if posts:
        print(f"第一筆: {posts[0]['record_id']}")

    print("\n✅ 所有測試完成！")
    print(f"請檢查 test_data/ 目錄")
