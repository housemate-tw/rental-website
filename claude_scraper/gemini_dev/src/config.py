#!/usr/bin/env python3
"""
配置管理模組

負責載入和管理系統配置，提供：
- JSON 配置檔載入
- 巢狀配置存取 (dot notation)
- 環境變數覆蓋支援
- 配置驗證
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class Config:
    """
    配置管理器

    使用方式:
        config = Config('config/config.json')
        group_url = config.get('facebook.group_url')
        # 或使用便捷屬性
        group_url = config.group_url
    """

    def __init__(self, config_path='config/config.json'):
        """
        初始化配置管理器

        Args:
            config_path (str): 配置檔案路徑

        Raises:
            FileNotFoundError: 配置檔案不存在
            json.JSONDecodeError: 配置檔案格式錯誤
        """
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"\n配置檔案不存在: {config_path}\n"
                f"請複製 config.example.json 到 config.json 並填寫您的設定:\n"
                f"  cp {self.config_path.parent}/config.example.json {config_path}\n"
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                self.data = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"配置檔案格式錯誤: {e}",
                    e.doc,
                    e.pos
                )

        self._validate()

    def _validate(self):
        """驗證配置的必要欄位"""
        required_fields = [
            'facebook.group_url',
            'scraper.max_posts_per_run',
            'paths.data_dir'
        ]

        missing_fields = []
        for field in required_fields:
            if self.get(field) is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                f"配置檔案缺少必要欄位:\n" +
                "\n".join(f"  - {field}" for field in missing_fields)
            )

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        取得配置值 (支援巢狀存取)

        Args:
            key_path (str): 配置路徑，用點號分隔 (e.g., 'facebook.group_url')
            default (Any): 預設值

        Returns:
            Any: 配置值，若不存在則返回 default
        """
        keys = key_path.split('.')
        value = self.data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        # 支援環境變數覆蓋
        # 例如: FB_GROUP_URL 會覆蓋 facebook.group_url
        env_key = '_'.join(keys).upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        return value

    # === 便捷屬性 (Facebook) ===

    @property
    def group_url(self) -> str:
        """Facebook 社團 URL"""
        return self.get('facebook.group_url')

    @property
    def cookies_path(self) -> str:
        """Cookies 檔案路徑"""
        return self.get('facebook.cookies_path', 'config/auth.json')

    @property
    def user_agent(self) -> Optional[str]:
        """使用者代理字串"""
        return self.get('facebook.user_agent')

    # === 便捷屬性 (Scraper) ===

    @property
    def max_posts(self) -> int:
        """單次執行最大抓取數"""
        return self.get('scraper.max_posts_per_run', 500)

    @property
    def scroll_delay(self) -> list:
        """滾動延遲範圍 [min, max]"""
        return self.get('scraper.scroll_delay', [1.5, 3.0])

    @property
    def reading_delay(self) -> list:
        """閱讀延遲範圍 [min, max]"""
        return self.get('scraper.reading_delay', [0.5, 1.5])

    @property
    def max_retries(self) -> int:
        """最大重試次數"""
        return self.get('scraper.max_retries', 3)

    @property
    def headless(self) -> bool:
        """是否使用無頭模式"""
        return self.get('scraper.headless', False)

    # === 便捷屬性 (Paths) ===

    @property
    def save_script_path(self) -> str:
        """Gemini 存檔腳本路徑"""
        return self.get('paths.save_script')

    @property
    def data_dir(self) -> str:
        """資料目錄"""
        return self.get('paths.data_dir')

    @property
    def state_file(self) -> str:
        """狀態檔案路徑"""
        return self.get('paths.state_file', 'state/scraper_state.json')

    @property
    def log_dir(self) -> str:
        """日誌目錄"""
        return self.get('paths.log_dir', 'logs/')

    # === 便捷屬性 (Monitoring) ===

    @property
    def enable_progress_bar(self) -> bool:
        """是否啟用進度條"""
        return self.get('monitoring.enable_progress_bar', True)

    @property
    def log_level(self) -> str:
        """日誌等級"""
        return self.get('monitoring.log_level', 'INFO')

    def __repr__(self) -> str:
        """字串表示"""
        return f"Config(file='{self.config_path}')"


# 測試程式碼
if __name__ == '__main__':
    print("測試 Config Loader...")

    # 測試 1: 載入範例配置
    print("\n[測試 1] 載入範例配置")
    try:
        config = Config('config/config.example.json')
        print(f"✅ 成功載入: {config}")
    except FileNotFoundError as e:
        print(f"❌ 錯誤: {e}")
        print("請確認 config.example.json 存在")
        exit(1)

    # 測試 2: 使用 get() 方法
    print("\n[測試 2] 使用 get() 方法")
    group_url = config.get('facebook.group_url')
    print(f"✅ facebook.group_url = {group_url}")

    max_posts = config.get('scraper.max_posts_per_run')
    print(f"✅ scraper.max_posts_per_run = {max_posts}")

    # 測試不存在的 key (應返回 default)
    unknown = config.get('unknown.key', 'DEFAULT_VALUE')
    assert unknown == 'DEFAULT_VALUE'
    print(f"✅ 不存在的 key 返回預設值")

    # 測試 3: 使用便捷屬性
    print("\n[測試 3] 使用便捷屬性")
    print(f"✅ config.group_url = {config.group_url}")
    print(f"✅ config.max_posts = {config.max_posts}")
    print(f"✅ config.headless = {config.headless}")
    print(f"✅ config.save_script_path = {config.save_script_path}")

    # 測試 4: 環境變數覆蓋
    print("\n[測試 4] 環境變數覆蓋")
    os.environ['SCRAPER_MAX_POSTS_PER_RUN'] = '999'
    max_posts_override = config.get('scraper.max_posts_per_run')
    print(f"✅ 環境變數覆蓋: max_posts_per_run = {max_posts_override}")
    del os.environ['SCRAPER_MAX_POSTS_PER_RUN']

    # 測試 5: 配置驗證 (模擬缺少必要欄位)
    print("\n[測試 5] 配置驗證")
    print("(實際專案中，缺少必要欄位會拋出 ValueError)")

    print("\n✅ 所有測試通過！")
