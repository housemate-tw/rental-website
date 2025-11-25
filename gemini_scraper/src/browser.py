#!/usr/bin/env python3
"""
瀏覽器控制模組

負責管理 Playwright 瀏覽器的生命週期和操作，提供：
- 瀏覽器啟動與關閉
- Cookie 管理 (登入狀態持久化)
- 頁面導航
- 滾動與等待操作
- 元素查找
"""

import time
import random
from pathlib import Path
from typing import Optional, List
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class BrowserController:
    """
    瀏覽器控制器

    使用方式:
        browser = BrowserController(config, logger)
        browser.launch(headless=False)
        browser.create_context(cookies_path='config/auth.json')
        browser.goto('https://www.facebook.com')
        browser.scroll_to_bottom()
        browser.close()
    """

    def __init__(self, config, logger):
        """
        初始化瀏覽器控制器

        Args:
            config: Config 物件
            logger: ScraperLogger 物件
        """
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def launch(self, headless: bool = False):
        """
        啟動瀏覽器

        Args:
            headless (bool): 是否使用無頭模式
        """
        self.logger.info(f"啟動瀏覽器 (headless={headless})...")

        try:
            self.playwright = sync_playwright().start()

            # 啟動 Chromium - 使用更多反檢測參數
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                ]
            )

            self.logger.info("✅ 瀏覽器啟動成功")

        except Exception as e:
            self.logger.error(f"啟動瀏覽器失敗: {e}", exc_info=True)
            raise

    def create_context(self, cookies_path: Optional[str] = None):
        """
        建立瀏覽器 context

        Args:
            cookies_path (str, optional): Cookies 檔案路徑
        """
        try:
            # 檢查是否有 cookies
            if cookies_path and Path(cookies_path).exists():
                self.logger.info(f"載入 Cookies: {cookies_path}")

                self.context = self.browser.new_context(
                    storage_state=cookies_path,
                    user_agent=self.config.user_agent,
                    viewport={'width': 1280, 'height': 720},
                    locale='zh-TW'
                )

                self.logger.info("✅ 使用現有登入狀態")

            else:
                self.logger.warning("未找到 Cookies，需要手動登入")

                self.context = self.browser.new_context(
                    user_agent=self.config.user_agent,
                    viewport={'width': 1280, 'height': 720},
                    locale='zh-TW'
                )

            # 建立頁面
            self.page = self.context.new_page()

            # 設定預設 timeout
            self.page.set_default_timeout(30000)  # 30 秒

            # 注入反檢測 JavaScript
            self._inject_stealth_scripts()

            self.logger.info("✅ Context 建立成功")

        except Exception as e:
            self.logger.error(f"建立 Context 失敗: {e}", exc_info=True)
            raise

    def _inject_stealth_scripts(self):
        """
        注入反檢測 JavaScript，避免被 Facebook 識別為機器人
        """
        try:
            # 移除 webdriver 標記
            self.page.add_init_script("""
                // 覆蓋 navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // 覆蓋 chrome 物件
                window.chrome = {
                    runtime: {}
                };

                // 覆蓋 permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // 覆蓋 plugins 長度
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // 覆蓋 languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-TW', 'zh', 'en-US', 'en']
                });
            """)
            self.logger.debug("✅ 反檢測腳本已注入")

        except Exception as e:
            self.logger.warning(f"注入反檢測腳本失敗: {e}")
            # 失敗不中斷，繼續執行

    def save_cookies(self, path: str):
        """
        儲存 Cookies (登入狀態)

        Args:
            path (str): 儲存路徑
        """
        try:
            # 確保目錄存在
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            self.context.storage_state(path=path)
            self.logger.info(f"✅ Cookies 已儲存: {path}")

        except Exception as e:
            self.logger.error(f"儲存 Cookies 失敗: {e}", exc_info=True)
            raise

    def goto(self, url: str, wait_until: str = 'domcontentloaded'):
        """
        導航到指定 URL

        Args:
            url (str): 目標 URL
            wait_until (str): 等待條件 ('load', 'domcontentloaded', 'networkidle')
                             預設使用 'domcontentloaded' 以避免 Facebook 等動態網站的超時問題
        """
        try:
            self.logger.info(f"導航到: {url}")
            # 對於 Facebook 這類持續載入內容的網站，使用 domcontentloaded 更穩定
            self.page.goto(url, wait_until=wait_until, timeout=90000)
            self.logger.info("✅ 頁面載入完成")

            # 額外等待一下，確保 JavaScript 渲染完成
            import time
            time.sleep(2)

        except Exception as e:
            self.logger.error(f"導航失敗: {e}", exc_info=True)
            raise

    def scroll_to_bottom(self, delay: Optional[float] = None) -> bool:
        """
        滾動到頁面底部

        Args:
            delay (float, optional): 滾動後等待時間 (秒)

        Returns:
            bool: 是否有新內容載入 (頁面高度是否增加)
        """
        try:
            # 如果沒有指定 delay，使用配置的隨機範圍
            if delay is None:
                delay_range = self.config.scroll_delay
                delay = random.uniform(delay_range[0], delay_range[1])

            # 取得當前頁面高度
            old_height = self.page.evaluate("document.body.scrollHeight")

            # 滾動到底部
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # 等待新內容載入
            time.sleep(delay)

            # 取得新的頁面高度
            new_height = self.page.evaluate("document.body.scrollHeight")

            has_new_content = new_height > old_height

            if has_new_content:
                self.logger.debug(f"頁面高度: {old_height} → {new_height} (+{new_height - old_height}px)")
            else:
                self.logger.debug("頁面高度未改變，可能已到底")

            return has_new_content

        except Exception as e:
            self.logger.error(f"滾動失敗: {e}", exc_info=True)
            return False

    def wait_for_selector(self, selector: str, timeout: int = 30000) -> bool:
        """
        等待元素出現

        Args:
            selector (str): CSS 選擇器
            timeout (int): 超時時間 (毫秒)

        Returns:
            bool: 元素是否出現
        """
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True

        except Exception as e:
            self.logger.warning(f"等待元素超時: {selector}")
            return False

    def query_selector(self, selector: str):
        """
        查找單一元素

        Args:
            selector (str): CSS 選擇器

        Returns:
            ElementHandle or None
        """
        try:
            return self.page.query_selector(selector)
        except Exception as e:
            self.logger.error(f"查找元素失敗: {selector}, {e}")
            return None

    def query_selector_all(self, selector: str) -> List:
        """
        查找所有符合的元素

        Args:
            selector (str): CSS 選擇器

        Returns:
            List[ElementHandle]
        """
        try:
            return self.page.query_selector_all(selector)
        except Exception as e:
            self.logger.error(f"查找元素失敗: {selector}, {e}")
            return []

    def is_logged_in(self) -> bool:
        """
        檢查是否已登入 Facebook

        Returns:
            bool: 是否已登入
        """
        try:
            # 方法 1: 檢查是否存在使用者選單 (支援多語言)
            selectors = [
                '[aria-label*="Account"]',      # 英文
                '[aria-label*="帳號"]',          # 繁體中文
                '[aria-label*="账号"]',          # 簡體中文
                '[aria-label*="個人檔案"]',      # 繁體中文
                '[aria-label*="个人主页"]',      # 簡體中文
                '[aria-label*="你的個人檔案"]',  # 繁體中文
                '[aria-label*="你的个人主页"]',  # 簡體中文
            ]

            for selector in selectors:
                element = self.page.query_selector(selector)
                if element:
                    self.logger.debug(f"✅ 找到登入元素: {selector}")
                    return True

            # 方法 2: 檢查是否有登入按鈕 (反向檢測 - 有登入按鈕表示未登入)
            login_button = self.page.query_selector('a[href*="login"]')
            if login_button:
                self.logger.debug("❌ 找到登入按鈕，表示未登入")
                return False

            # 方法 3: 檢查 URL 是否包含 login (如果跳轉到登入頁面)
            if 'login' in self.page.url.lower():
                self.logger.debug("❌ URL 包含 'login'，表示在登入頁面")
                return False

            # 如果都沒有明確證據，再嘗試其他方法
            # 檢查導航欄是否存在（登入後才有完整導航欄）
            nav_selectors = [
                'div[role="navigation"]',
                'nav',
                '[aria-label*="主導覽"]',
                '[aria-label*="Primary Navigation"]',
            ]

            for selector in nav_selectors:
                nav = self.page.query_selector(selector)
                if nav:
                    self.logger.debug(f"✅ 找到導航欄: {selector}")
                    # 還要確認導航欄內有足夠的內容（不是空的）
                    if len(nav.inner_text()) > 10:
                        return True

            self.logger.warning("⚠️ 無法確定登入狀態，假設未登入")
            return False

        except Exception as e:
            self.logger.error(f"檢查登入狀態失敗: {e}")
            return False

    def take_screenshot(self, path: str):
        """
        截圖 (用於除錯)

        Args:
            path (str): 儲存路徑
        """
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=path)
            self.logger.info(f"截圖已儲存: {path}")

        except Exception as e:
            self.logger.error(f"截圖失敗: {e}")

    def close(self):
        """關閉瀏覽器"""
        try:
            if self.context:
                self.context.close()
                self.logger.debug("Context 已關閉")

            if self.browser:
                self.browser.close()
                self.logger.debug("Browser 已關閉")

            if self.playwright:
                self.playwright.stop()
                self.logger.debug("Playwright 已停止")

            self.logger.info("✅ 瀏覽器已關閉")

        except Exception as e:
            self.logger.error(f"關閉瀏覽器時出錯: {e}")


# 測試程式碼
if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    from config import Config
    from logger import ScraperLogger

    print("=" * 60)
    print("Browser Controller 互動測試")
    print("=" * 60)
    print()
    print("⚠️  這個測試會開啟真實的瀏覽器視窗")
    print()

    # 初始化
    config = Config('config/config.example.json')
    logger = ScraperLogger('test_logs/')
    browser = BrowserController(config, logger)

    try:
        # 測試 1: 啟動瀏覽器
        print("\n[測試 1] 啟動瀏覽器")
        browser.launch(headless=False)
        print("✅ 瀏覽器已啟動")

        # 測試 2: 建立 Context
        print("\n[測試 2] 建立 Context")
        browser.create_context()
        print("✅ Context 已建立")

        # 測試 3: 導航到 Facebook
        print("\n[測試 3] 導航到 Facebook")
        browser.goto('https://www.facebook.com')
        print("✅ 已導航到 Facebook")

        # 測試 4: 檢查登入狀態
        print("\n[測試 4] 檢查登入狀態")
        is_logged_in = browser.is_logged_in()
        if is_logged_in:
            print("✅ 已登入")
        else:
            print("⚠️  未登入 (這是正常的，因為沒有 Cookies)")
            print("\n如需測試登入功能，請:")
            print("1. 在瀏覽器中手動登入 Facebook")
            print("2. 按 Enter 繼續...")
            input()

            # 儲存 Cookies
            print("\n[測試 5] 儲存 Cookies")
            browser.save_cookies('test_logs/test_auth.json')
            print("✅ Cookies 已儲存")

            # 重新載入 Cookies
            print("\n[測試 6] 重新載入 Cookies")
            browser.close()
            browser.launch(headless=False)
            browser.create_context(cookies_path='test_logs/test_auth.json')
            browser.goto('https://www.facebook.com')

            if browser.is_logged_in():
                print("✅ 使用 Cookies 登入成功！")
            else:
                print("❌ Cookies 登入失敗")

        # 測試 7: 滾動測試
        print("\n[測試 7] 滾動測試 (3 次)")
        for i in range(3):
            has_new = browser.scroll_to_bottom()
            print(f"  滾動 {i+1}/3: {'有新內容' if has_new else '無新內容'}")
            time.sleep(1)

        # 測試 8: 截圖
        print("\n[測試 8] 截圖")
        browser.take_screenshot('test_logs/test_screenshot.png')
        print("✅ 截圖已儲存")

        print("\n" + "=" * 60)
        print("✅ 所有測試完成！")
        print("=" * 60)
        print("\n按 Enter 關閉瀏覽器...")
        input()

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")

    finally:
        browser.close()
