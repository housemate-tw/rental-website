#!/usr/bin/env python3
"""
終極調試：使用 JavaScript 在瀏覽器中尋找真正的貼文
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from logger import ScraperLogger
from browser import BrowserController

def main():
    print("🔍 尋找真正的貼文元素")
    print("=" * 60)

    config = Config('config/config.json')
    logger = ScraperLogger('logs/')
    browser = BrowserController(config, logger)

    try:
        print("\n1. 啟動瀏覽器...")
        browser.launch(headless=False)

        print("2. 載入 Cookies...")
        browser.create_context(cookies_path='config/auth.json')

        print("3. 前往社團頁面...")
        browser.goto(config.group_url)

        page = browser.page

        print("\n4. 滾動到頁面頂部...")
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        print("5. 稍微滾動以觸發內容載入...")
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(2)
        page.evaluate("window.scrollBy(0, -500)")
        time.sleep(2)

        print("\n✅ 開始分析...\n")
        print("="*60)

        # 使用 JavaScript 找到所有包含長文本（>20字元）的元素
        result = page.evaluate("""() => {
            const MIN_TEXT_LENGTH = 20;  // 降低門檻
            const results = [];

            // 遍歷所有元素
            function findTextElements(element, depth = 0) {
                if (depth > 15) return;  // 限制深度

                // 獲取直接文本（不包括子元素）
                const directText = Array.from(element.childNodes)
                    .filter(node => node.nodeType === Node.TEXT_NODE)
                    .map(node => node.textContent.trim())
                    .join(' ');

                // 獲取所有文本（包括子元素）
                const allText = element.innerText || '';

                // 如果這個元素有足夠長的文本
                if (allText.length > MIN_TEXT_LENGTH) {
                    // 找到貼文的永久連結
                    const permalink = element.querySelector('a[href*="/posts/"], a[href*="/permalink/"]');

                    results.push({
                        tagName: element.tagName,
                        className: element.className || '',
                        id: element.id || '',
                        textLength: allText.length,
                        textPreview: allText.substring(0, 150),
                        hasPermalink: !!permalink,
                        permalinkHref: permalink ? permalink.href : '',
                        role: element.getAttribute('role') || '',
                        depth: depth
                    });
                }

                // 遞迴處理子元素（但跳過已經找到的）
                if (allText.length < MIN_TEXT_LENGTH * 2) {
                    Array.from(element.children).forEach(child => {
                        findTextElements(child, depth + 1);
                    });
                }
            }

            // 從 body 開始搜索
            findTextElements(document.body);

            // 按文本長度排序，最長的在前面
            results.sort((a, b) => b.textLength - a.textLength);

            return results.slice(0, 30);  // 返回前30個
        }""")

        print(f"找到 {len(result)} 個可能的貼文元素：\n")

        for i, elem in enumerate(result, 1):
            print(f"{'─'*60}")
            print(f"元素 #{i}")
            print(f"{'─'*60}")
            print(f"標籤: <{elem['tagName'].lower()}>")
            print(f"Class: {elem['className'][:100]}...")
            print(f"ID: {elem['id']}")
            print(f"Role: {elem['role']}")
            print(f"深度: {elem['depth']}")
            print(f"文本長度: {elem['textLength']} 字元")
            print(f"有永久連結: {'✅' if elem['hasPermalink'] else '❌'}")
            if elem['hasPermalink']:
                print(f"連結: {elem['permalinkHref'][:80]}...")
            print(f"\n文本預覽:")
            print(f"  {elem['textPreview']}...\n")

        print("="*60)
        print("✅ 分析完成！")
        print("="*60)
        print("\n💡 根據上面的結果：")
        print("1. 找出哪些是真正的租屋貼文（文本最長、有永久連結的）")
        print("2. 記下它們的 tagName, className, role 等特徵")
        print("3. 這些特徵可以用來改進爬蟲的選擇器")
        print("\n按 Enter 關閉...")
        input()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

    finally:
        browser.close()
        print("\n👋 結束")

if __name__ == '__main__':
    main()
