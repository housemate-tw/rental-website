#!/usr/bin/env python3
"""
調試腳本：尋找真正的貼文（不是留言）
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from logger import ScraperLogger
from browser import BrowserController

def main():
    print("🔍 Facebook 貼文偵測工具")
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

        page = browser.page

        print("\n4. 滾動到頁面頂部...")
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        print("\n✅ 頁面已載入，開始分析...")
        print("-" * 60)

        # 策略 1: 尋找可能的貼文容器
        print("\n📦 策略 1: 尋找貼文容器")
        print("-" * 60)

        # Facebook 群組通常有一個 feed 容器
        possible_containers = [
            'div[role="feed"]',
            'div[role="main"]',
            'div[data-pagelet="GroupFeed"]',
            '[id*="pagelet"]',
        ]

        for selector in possible_containers:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"✅ 找到 {len(elements)} 個: {selector}")
            else:
                print(f"❌ 未找到: {selector}")

        # 策略 2: 分析 role="article" 的父元素
        print("\n\n📊 策略 2: 分析所有 role='article' 元素")
        print("-" * 60)

        articles = page.query_selector_all('[role="article"]')
        print(f"總共找到 {len(articles)} 個 [role='article']\n")

        for i, article in enumerate(articles[:10], 1):
            print(f"\n{'─'*60}")
            print(f"元素 #{i}")
            print(f"{'─'*60}")

            # 獲取文本前 100 字元
            full_text = article.inner_text()[:100].replace('\n', ' ')
            print(f"📝 文本: {full_text}...")
            print(f"📏 長度: {len(article.inner_text())} 字元")

            # 檢查是否有作者資訊（主貼文通常有）
            author_links = article.query_selector_all('a[role="link"]')
            if author_links:
                first_author = author_links[0].inner_text().strip()
                print(f"👤 第一個連結: {first_author}")

            # 檢查是否有時間戳記
            time_elem = article.query_selector('abbr, time')
            if time_elem:
                print(f"⏰ 有時間元素")

            # 檢查是否有永久連結
            permalink = article.query_selector('a[href*="/posts/"], a[href*="/permalink/"]')
            if permalink:
                href = permalink.get_attribute('href')
                print(f"🔗 永久連結: {href[:80]}...")

            # 檢查層級深度（主貼文通常在較淺的層級）
            # 使用 JavaScript 計算距離 body 的深度
            depth = page.evaluate("""(element) => {
                let depth = 0;
                let current = element;
                while (current && current.tagName !== 'BODY') {
                    depth++;
                    current = current.parentElement;
                }
                return depth;
            }""", article)
            print(f"📊 DOM 深度: {depth}")

            # 檢查是否在留言區內（留言通常在特定的容器內）
            is_in_comment_section = page.evaluate("""(element) => {
                let current = element;
                while (current) {
                    const classList = current.className || '';
                    const id = current.id || '';
                    // 檢查是否在留言區相關的容器內
                    if (classList.includes('comment') ||
                        id.includes('comment') ||
                        classList.includes('reply')) {
                        return true;
                    }
                    current = current.parentElement;
                }
                return false;
            }""", article)
            print(f"💬 在留言區內: {'是' if is_in_comment_section else '否'}")

        # 策略 3: 截圖整個頁面
        print("\n\n📸 策略 3: 截圖頁面")
        print("-" * 60)
        page.screenshot(path="logs/debug_full_page.png", full_page=True)
        print("✅ 完整頁面截圖: logs/debug_full_page.png")

        # 截圖可見區域
        page.screenshot(path="logs/debug_viewport.png")
        print("✅ 可見區域截圖: logs/debug_viewport.png")

        print("\n" + "="*60)
        print("✅ 分析完成！")
        print("="*60)
        print("\n💡 建議：")
        print("1. 查看截圖 logs/debug_full_page.png")
        print("2. 找出主貼文的特徵（長度、深度、是否有永久連結）")
        print("3. 排除留言（通常在留言區內、文本較短）")
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
