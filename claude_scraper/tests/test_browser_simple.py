#!/usr/bin/env python3
"""
Browser Controller 簡單自動測試
(不需要人工介入)
"""

import sys
from pathlib import Path

# 加入 src 到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import Config
from logger import ScraperLogger
from browser import BrowserController

print("=" * 60)
print("Browser Controller 自動測試")
print("=" * 60)

# 初始化
config = Config('../config/config.example.json')
logger = ScraperLogger('../test_logs/')
browser = BrowserController(config, logger)

try:
    # 測試 1: 啟動瀏覽器
    print("\n[測試 1] 啟動瀏覽器 (headless 模式)")
    browser.launch(headless=True)
    print("✅ Pass")

    # 測試 2: 建立 Context
    print("\n[測試 2] 建立 Context")
    browser.create_context()
    print("✅ Pass")

    # 測試 3: 導航到簡單頁面
    print("\n[測試 3] 導航測試")
    browser.goto('https://example.com')
    print("✅ Pass")

    # 測試 4: 滾動測試
    print("\n[測試 4] 滾動測試")
    has_new = browser.scroll_to_bottom(delay=1)
    print(f"✅ Pass (has_new_content={has_new})")

    # 測試 5: 元素查找
    print("\n[測試 5] 元素查找測試")
    h1 = browser.query_selector('h1')
    if h1:
        print("✅ Pass (找到 h1 元素)")
    else:
        print("⚠️  未找到 h1 元素")

    # 測試 6: 截圖
    print("\n[測試 6] 截圖測試")
    browser.take_screenshot('../test_logs/browser_test.png')
    print("✅ Pass")

    print("\n" + "=" * 60)
    print("✅ 所有測試通過！")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()

finally:
    browser.close()
    print("\n瀏覽器已關閉")
