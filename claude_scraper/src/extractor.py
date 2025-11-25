#!/usr/bin/env python3
"""
貼文提取模組

負責從 Facebook 頁面提取貼文資料，提供：
- 識別頁面上的貼文元素
- 提取貼文 ID
- 提取貼文內容
- 提取貼文 URL
- 提取時間戳
"""

import hashlib
import re
from typing import Optional, Dict, List
from datetime import datetime


class PostExtractor:
    """
    貼文提取器

    使用方式:
        extractor = PostExtractor(logger)
        posts = extractor.extract_posts(page)
        for post in posts:
            data = extractor.extract_post_data(post)
            if data:
                print(data)
    """

    def __init__(self, logger):
        """
        初始化貼文提取器

        Args:
            logger: ScraperLogger 物件
        """
        self.logger = logger

    def extract_posts(self, page) -> List:
        """
        提取頁面上所有可見的貼文元素

        Args:
            page: Playwright Page 物件

        Returns:
            List: 貼文元素列表
        """
        try:
            # Facebook 使用 role="article" 標記貼文
            posts = page.query_selector_all('[role="article"]')
            self.logger.debug(f"找到 {len(posts)} 個貼文元素")
            return posts

        except Exception as e:
            self.logger.error(f"提取貼文列表失敗: {e}", exc_info=True)
            return []

    def extract_post_data(self, post_element) -> Optional[Dict]:
        """
        從貼文元素提取所有需要的資料

        Args:
            post_element: Playwright ElementHandle

        Returns:
            Optional[Dict]: 貼文資料，若提取失敗則為 None
            {
                'id': str,          # 貼文唯一 ID
                'text': str,        # 貼文文本內容
                'url': str,         # 貼文連結
                'timestamp': str,   # 發布時間 (如有)
                'author': str,      # 作者 (如有)
            }
        """
        try:
            # 0. 先檢查這是否是留言（不是主貼文）
            # 留言的永久連結包含 ?comment 參數
            url = self._extract_url(post_element)
            if url and '?comment' in url:
                self.logger.debug(f"跳過：這是留言，不是主貼文 (URL: {url[:80]})")
                return None

            # 1. 展開「查看更多」按鈕（如果有的話）
            self._expand_see_more(post_element)

            # 2. 提取文本內容
            text = self._extract_text(post_element)

            if not text or len(text.strip()) < 5:
                self.logger.debug(f"跳過：貼文文本過短 (僅 {len(text)} 字元): '{text[:50]}'")
                return None

            # URL 已經在步驟 0 提取過了

            # 3. 提取貼文 ID
            post_id = self._extract_post_id(post_element, url, text)

            # 4. 提取時間戳 (選用)
            timestamp = self._extract_timestamp(post_element)

            # 5. 提取作者 (選用)
            author = self._extract_author(post_element)

            return {
                'id': post_id,
                'text': text,
                'url': url,
                'timestamp': timestamp,
                'author': author,
                'extracted_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"提取貼文資料失敗: {e}", exc_info=True)
            return None

    def _expand_see_more(self, element):
        """
        展開「查看更多」按鈕，顯示完整貼文內容

        Args:
            element: Playwright ElementHandle
        """
        try:
            import time

            # 多種「查看更多」的可能文字（支援多語言）
            see_more_texts = [
                'See more',
                'See More',
                '查看更多',
                '顯示更多',
                '显示更多',
                'Xem thêm',  # 越南文
                'もっと見る',  # 日文
            ]

            # 方法 1: 尋找所有可能的按鈕元素
            button_selectors = [
                'div[role="button"]',
                'span[role="button"]',
            ]

            for btn_selector in button_selectors:
                buttons = element.query_selector_all(btn_selector)
                self.logger.debug(f"找到 {len(buttons)} 個按鈕元素 ({btn_selector})")

                for i, button in enumerate(buttons):
                    try:
                        button_text = button.inner_text().strip()
                        self.logger.debug(f"  按鈕 {i+1} 文字: '{button_text[:50]}'")

                        # 檢查按鈕文字是否匹配
                        if any(see_more in button_text for see_more in see_more_texts):
                            if button.is_visible():
                                self.logger.debug(f"✅ 找到「查看更多」按鈕: {button_text}")
                                button.click()
                                # 等待內容展開
                                time.sleep(0.5)
                                self.logger.debug("✅ 已展開貼文內容")
                                return
                    except Exception as e:
                        self.logger.debug(f"  按鈕 {i+1} 檢查失敗: {e}")
                        continue

            # 方法 2: 使用 XPath 尋找包含特定文字的元素
            for text in see_more_texts:
                try:
                    # 使用 XPath 來尋找包含特定文字的元素
                    xpath = f".//*[@role='button' and contains(text(), '{text}')]"
                    see_more_btn = element.query_selector(f'xpath={xpath}')
                    if see_more_btn and see_more_btn.is_visible():
                        self.logger.debug(f"找到「查看更多」按鈕 (XPath): {text}")
                        see_more_btn.click()
                        time.sleep(0.5)
                        self.logger.debug("✅ 已展開貼文內容")
                        return
                except Exception:
                    continue

            # 如果沒有找到「查看更多」按鈕，表示內容已經是完整的
            self.logger.debug("未找到「查看更多」按鈕，可能內容已完整展開")

        except Exception as e:
            self.logger.debug(f"展開「查看更多」失敗: {e}")
            # 即使失敗也繼續，因為可能本來就沒有「查看更多」按鈕

    def _extract_text(self, element) -> str:
        """
        提取貼文文本內容

        Args:
            element: Playwright ElementHandle

        Returns:
            str: 貼文文本
        """
        try:
            # Facebook 貼文內容的多種可能選擇器（優先順序從高到低）
            selectors = [
                # 新版 Facebook 選擇器
                'div[data-ad-comet-preview="message"]',
                'div[data-ad-preview="message"]',
                '[data-ad-rendering-role="story_message"]',

                # 通用選擇器 - 貼文內容通常在 dir="auto" 的 div 中
                'div[dir="auto"][style*="text-align"]',

                # 更寬鬆的選擇器
                'div[dir="auto"]',
            ]

            # 先嘗試精確選擇器
            for selector in selectors[:3]:
                text_elem = element.query_selector(selector)
                if text_elem:
                    text = text_elem.inner_text()
                    if text and len(text.strip()) > 10:
                        self.logger.debug(f"✅ 使用 selector: {selector}, 提取到 {len(text)} 字元")
                        return text.strip()

            # 如果精確選擇器失敗，嘗試找所有 dir="auto" 的元素
            # 通常第一個長文本就是貼文內容
            all_divs = element.query_selector_all('div[dir="auto"]')
            for div in all_divs:
                text = div.inner_text()
                if text and len(text.strip()) > 30:  # 至少要有 30 字元才算是貼文
                    self.logger.debug(f"✅ 使用 fallback，提取到 {len(text)} 字元")
                    return text.strip()

            # 最終 fallback：獲取整個元素的文本（但這通常包含太多雜訊）
            fallback_text = element.inner_text()
            self.logger.debug(f"⚠️ 使用 full text fallback，提取到 {len(fallback_text)} 字元")

            # 如果文本太短，記錄警告
            if len(fallback_text.strip()) < 10:
                self.logger.debug(f"❌ 提取的文本太短: '{fallback_text[:100]}'")

            return fallback_text.strip() if fallback_text else ""

        except Exception as e:
            self.logger.debug(f"提取文本失敗: {e}")
            return ""

    def _extract_url(self, element) -> str:
        """
        提取貼文永久連結

        Args:
            element: Playwright ElementHandle

        Returns:
            str: 貼文 URL
        """
        try:
            # 尋找包含 /posts/ 或 /permalink/ 的連結
            selectors = [
                'a[href*="/posts/"]',
                'a[href*="/permalink/"]',
                'a[href*="story_fbid"]',
            ]

            for selector in selectors:
                link = element.query_selector(selector)
                if link:
                    href = link.get_attribute('href')
                    if href:
                        # 補全為完整 URL
                        if href.startswith('/'):
                            return f"https://www.facebook.com{href}"
                        elif href.startswith('http'):
                            # 清理 URL 參數
                            return href.split('?')[0]

            return ""

        except Exception as e:
            self.logger.debug(f"提取 URL 失敗: {e}")
            return ""

    def _extract_post_id(self, element, url: str, text: str) -> str:
        """
        提取或生成貼文 ID

        Args:
            element: Playwright ElementHandle
            url (str): 貼文 URL
            text (str): 貼文文本

        Returns:
            str: 貼文 ID
        """
        try:
            # 方法 1: 從 URL 提取 ID
            if url:
                # 嘗試從 URL 中提取數字 ID
                # 例如: /posts/123456789 或 /permalink/123456789
                match = re.search(r'/(?:posts|permalink)/(\d+)', url)
                if match:
                    return match.group(1)

                # 嘗試從 story_fbid 參數提取
                match = re.search(r'story_fbid=(\d+)', url)
                if match:
                    return match.group(1)

            # 方法 2: 從元素屬性提取
            # Facebook 有時會在 data 屬性中包含 ID
            for attr in ['data-ft', 'data-testid', 'id']:
                value = element.get_attribute(attr)
                if value:
                    # 嘗試從屬性值中提取數字
                    match = re.search(r'\d{10,}', str(value))
                    if match:
                        return match.group(0)

            # 方法 3: 使用內容 hash 作為 ID (fallback)
            # 使用文本前 500 字元生成 hash
            content_sample = text[:500] if text else ""
            content_hash = hashlib.md5(content_sample.encode('utf-8')).hexdigest()
            return f"hash_{content_hash[:16]}"

        except Exception as e:
            self.logger.debug(f"提取 ID 失敗: {e}")
            # 最終 fallback
            return f"unknown_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _extract_timestamp(self, element) -> Optional[str]:
        """
        提取貼文時間戳

        Args:
            element: Playwright ElementHandle

        Returns:
            Optional[str]: 時間戳 (ISO 格式)
        """
        try:
            # 尋找時間元素 (通常是 <abbr> 或 <time>)
            time_elem = element.query_selector('abbr, time')
            if time_elem:
                # 嘗試獲取 data-utime 屬性 (Unix timestamp)
                utime = time_elem.get_attribute('data-utime')
                if utime:
                    timestamp = datetime.fromtimestamp(int(utime))
                    return timestamp.isoformat()

                # 嘗試獲取 datetime 屬性
                dt = time_elem.get_attribute('datetime')
                if dt:
                    return dt

                # 嘗試獲取 title 屬性 (完整日期)
                title = time_elem.get_attribute('title')
                if title:
                    return title

            return None

        except Exception as e:
            self.logger.debug(f"提取時間戳失敗: {e}")
            return None

    def _extract_author(self, element) -> Optional[str]:
        """
        提取貼文作者

        Args:
            element: Playwright ElementHandle

        Returns:
            Optional[str]: 作者名稱
        """
        try:
            # 尋找作者連結
            author_link = element.query_selector('a[role="link"]')
            if author_link:
                # 通常作者名稱在第一個連結的 aria-label 或文本中
                author_name = author_link.inner_text()
                if author_name and len(author_name.strip()) > 0:
                    return author_name.strip()

            return None

        except Exception as e:
            self.logger.debug(f"提取作者失敗: {e}")
            return None


# 測試程式碼
if __name__ == '__main__':
    print("PostExtractor 模組")
    print("此模組需要配合 BrowserController 使用")
    print("請執行主程式 scraper.py 進行完整測試")
