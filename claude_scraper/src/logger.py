#!/usr/bin/env python3
"""
日誌系統模組

提供結構化的日誌記錄功能，包括：
- 完整日誌記錄到檔案
- 錯誤日誌單獨記錄
- Console 輸出
- 自動日誌檔案輪替
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class ScraperLogger:
    """
    爬蟲日誌系統

    使用方式:
        logger = ScraperLogger('logs/')
        logger.info("開始執行爬蟲")
        logger.error("發生錯誤", exc_info=True)
    """

    def __init__(self, log_dir='logs/'):
        """
        初始化日誌系統

        Args:
            log_dir (str): 日誌目錄路徑
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 建立 archive 子目錄
        (self.log_dir / 'archive').mkdir(exist_ok=True)

        # 取得當天日期
        today = datetime.now().strftime('%Y%m%d')

        # 日誌檔案路徑
        self.main_log_file = self.log_dir / f'scraper_{today}.log'
        self.error_log_file = self.log_dir / f'error_{today}.log'

        # 建立 logger
        self.logger = logging.getLogger('scraper')
        self.logger.setLevel(logging.DEBUG)

        # 清除既有的 handlers (避免重複)
        self.logger.handlers.clear()

        # 1. 完整日誌 Handler (所有等級)
        fh_all = logging.FileHandler(
            self.main_log_file,
            encoding='utf-8'
        )
        fh_all.setLevel(logging.DEBUG)

        # 2. 錯誤日誌 Handler (只記錄 ERROR 以上)
        fh_error = logging.FileHandler(
            self.error_log_file,
            encoding='utf-8'
        )
        fh_error.setLevel(logging.ERROR)

        # 3. Console Handler (INFO 以上)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 設定格式
        # 格式: [時間] [等級] [模組] 訊息
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        fh_all.setFormatter(formatter)
        fh_error.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 添加 handlers
        self.logger.addHandler(fh_all)
        self.logger.addHandler(fh_error)
        self.logger.addHandler(ch)

        # 記錄初始化訊息
        self.logger.info("=" * 60)
        self.logger.info("Logger initialized")
        self.logger.info(f"Main log: {self.main_log_file}")
        self.logger.info(f"Error log: {self.error_log_file}")
        self.logger.info("=" * 60)

    def debug(self, message):
        """
        記錄 DEBUG 等級訊息

        Args:
            message (str): 訊息內容
        """
        self.logger.debug(message)

    def info(self, message):
        """
        記錄 INFO 等級訊息

        Args:
            message (str): 訊息內容
        """
        self.logger.info(message)

    def warning(self, message):
        """
        記錄 WARNING 等級訊息

        Args:
            message (str): 訊息內容
        """
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """
        記錄 ERROR 等級訊息

        Args:
            message (str): 訊息內容
            exc_info (bool): 是否包含完整的 exception 追蹤
        """
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        """
        記錄 CRITICAL 等級訊息

        Args:
            message (str): 訊息內容
            exc_info (bool): 是否包含完整的 exception 追蹤
        """
        self.logger.critical(message, exc_info=exc_info)

    def separator(self, char='-', length=60):
        """
        記錄分隔線 (用於區分不同階段)

        Args:
            char (str): 分隔字元
            length (int): 長度
        """
        self.logger.info(char * length)

    def section(self, title):
        """
        記錄區段標題

        Args:
            title (str): 標題
        """
        self.separator('=')
        self.logger.info(title)
        self.separator('=')


# 測試程式碼
if __name__ == '__main__':
    # 建立測試日誌
    print("測試 Logger System...")

    logger = ScraperLogger('test_logs/')

    # 測試各種等級
    logger.debug("這是 DEBUG 訊息 (只會出現在檔案)")
    logger.info("這是 INFO 訊息")
    logger.warning("這是 WARNING 訊息")
    logger.error("這是 ERROR 訊息")

    # 測試區段
    logger.section("測試區段")
    logger.info("區段內的訊息")

    # 測試 exception 記錄
    try:
        result = 1 / 0
    except Exception as e:
        logger.error("發生錯誤", exc_info=True)

    print(f"\n✅ 測試完成！")
    print(f"請檢查 test_logs/ 目錄:")
    print(f"- scraper_{datetime.now().strftime('%Y%m%d')}.log (完整日誌)")
    print(f"- error_{datetime.now().strftime('%Y%m%d')}.log (只有錯誤)")
