#!/usr/bin/env python3
"""
調試腳本：分析 Facebook 群組頁面結構
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from logger import ScraperLogger
from browser import BrowserController

def main():
    print("🔍 Facebook 頁面結構分析工具")
    print("=" * 60)

    # 初始化
    config = Config('config/config.json')
    logger = ScraperLogger('logs/')
    browser = BrowserController(config, logger)

    try:
        # 啟動瀏覽器
        print("\n1. 啟動瀏覽器...")
        browser.launch(headless=False)

        # 建立 context
        print("2. 載入 Cookies...")
        browser.create_context(cookies_path='config/auth.json')

        # 導航
        print("3. 前往社團頁面...")
        browser.goto(config.group_url)

        print("\n✅ 頁面已載入，現在開始分析...")
        print("-" * 60)

        # 分析頁面結構
        page = browser.page

        # 找所有 article 元素
        articles = page.query_selector_all('[role="article"]')
        print(f"\n📊 找到 {len(articles)} 個 [role='article'] 元素\n")

        for i, article in enumerate(articles[:5], 1):  # 只分析前 5 個
            print(f"\n{'='*60}")
            print(f"元素 #{i}")
            print(f"{'='*60}")

            # 獲取文本
            full_text = article.inner_text()
            print(f"📝 完整文本 ({len(full_text)} 字元):")
            print(f"   {full_text[:200]}...")

            # 檢查是否有「查看更多」
            buttons = article.query_selector_all('div[role="button"]')
            print(f"\n🔘 找到 {len(buttons)} 個按鈕:")
            for j, btn in enumerate(buttons[:10], 1):  # 只顯示前 10 個
                btn_text = btn.inner_text().strip()
                if btn_text:
                    print(f"   按鈕 {j}: '{btn_text[:50]}'")

            # 檢查 div[dir="auto"]
            divs = article.query_selector_all('div[dir="auto"]')
            print(f"\n📄 找到 {len(divs)} 個 div[dir='auto']:")
            for j, div in enumerate(divs[:5], 1):  # 只顯示前 5 個
                div_text = div.inner_text().strip()
                if len(div_text) > 10:
                    print(f"   Div {j} ({len(div_text)} 字元): {div_text[:80]}...")

            # 截圖
            screenshot_path = f"logs/debug_article_{i}.png"
            try:
                article.screenshot(path=screenshot_path)
                print(f"\n📸 截圖已儲存: {screenshot_path}")
            except Exception as e:
                print(f"\n⚠️ 截圖失敗: {e}")

        print("\n" + "="*60)
        print("✅ 分析完成！")
        print("="*60)
        print("\n按 Enter 關閉瀏覽器...")
        input()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

    finally:
        browser.close()
        print("\n👋 分析結束")

if __name__ == '__main__':
    main()
