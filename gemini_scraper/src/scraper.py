#!/usr/bin/env python3
"""
Facebook 租屋爬蟲主程式

整合所有模組，執行完整的爬取流程：
1. 啟動瀏覽器
2. 登入 Facebook (使用 Cookies)
3. 導航到目標社團
4. 滾動並提取貼文
5. 去重並儲存
6. 產生統計報告
"""

import sys
import time
import signal
from pathlib import Path
from typing import Optional

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from logger import ScraperLogger
from state_manager import StateManager
from browser import BrowserController
from extractor import PostExtractor
from saver import PostSaver


class FacebookScraper:
    """
    Facebook 租屋爬蟲主類別

    使用方式:
        scraper = FacebookScraper()
        scraper.run()
    """

    def __init__(self, config_path: str = 'config/config.json'):
        """
        初始化爬蟲

        Args:
            config_path (str): 配置檔案路徑
        """
        # 載入配置
        self.config = Config(config_path)

        # 初始化日誌
        self.logger = ScraperLogger(self.config.log_dir)
        self.logger.section("Facebook 租屋爬蟲 - Claude Scraper v1.0")

        # 初始化其他模組
        self.state = StateManager(self.config.state_file)
        self.browser = BrowserController(self.config, self.logger)
        self.extractor = PostExtractor(self.logger)
        self.saver = PostSaver(self.config.data_dir, self.logger)

        # Session 相關
        self.session_id: Optional[str] = None
        self.is_running = True

        # 註冊中斷信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """處理中斷信號 (Ctrl+C)"""
        self.logger.warning("\n⚠️  收到中斷信號，正在安全關閉...")
        self.is_running = False

    def run(self):
        """
        主執行流程
        """
        try:
            # 開始 session
            self.session_id = self.state.start_session()
            self.logger.info(f"Session ID: {self.session_id}")

            # 顯示配置資訊
            self._print_config()

            # 1. 啟動瀏覽器
            self.logger.separator()
            self.logger.info("步驟 1: 啟動瀏覽器")
            self.browser.launch(headless=self.config.headless)

            # 2. 建立 Context (載入 Cookies)
            self.logger.info("步驟 2: 建立瀏覽器 Context")
            cookies_path = self.config.cookies_path
            self.browser.create_context(cookies_path=cookies_path)

            # 3. 導航到目標社團
            self.logger.info("步驟 3: 導航到目標社團")
            self.browser.goto(self.config.group_url)

            # 等待頁面載入
            time.sleep(3)

            # 3.5. 滾動到頁面頂部並刷新，確保從乾淨狀態開始
            self.logger.info("步驟 3.5: 準備頁面")
            self.browser.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            # 4. 檢查登入狀態
            self.logger.info("步驟 4: 檢查登入狀態")

            # 先截圖以便調試
            debug_screenshot = f"logs/debug_before_login_{self.session_id}.png"
            self.browser.take_screenshot(debug_screenshot)
            self.logger.debug(f"調試截圖已儲存: {debug_screenshot}")

            if not self._check_and_handle_login():
                # 登入失敗時也截圖
                fail_screenshot = f"logs/debug_login_failed_{self.session_id}.png"
                self.browser.take_screenshot(fail_screenshot)
                self.logger.error(f"登入失敗，截圖已儲存: {fail_screenshot}")
                self.logger.error("登入失敗，無法繼續")
                return

            # 5. 執行爬取
            self.logger.separator()
            self.logger.info("步驟 5: 開始爬取貼文")
            self._scraping_loop()

            # 6. 結束
            self.state.end_session(self.session_id, 'completed')
            self.logger.separator()
            self.logger.info("✅ 爬取完成")

        except KeyboardInterrupt:
            self.logger.warning("使用者中斷")
            if self.session_id:
                self.state.end_session(self.session_id, 'interrupted')

        except Exception as e:
            self.logger.critical(f"發生嚴重錯誤: {e}", exc_info=True)
            if self.session_id:
                self.state.end_session(self.session_id, 'failed')

        finally:
            # 關閉瀏覽器
            self.browser.close()

            # 顯示摘要
            self._print_summary()

    def _print_config(self):
        """顯示配置資訊"""
        self.logger.info("配置資訊:")
        self.logger.info(f"  社團 URL: {self.config.group_url}")
        self.logger.info(f"  最大貼文數: {self.config.max_posts}")
        self.logger.info(f"  資料目錄: {self.config.data_dir}")
        self.logger.info(f"  無頭模式: {self.config.headless}")

    def _check_and_handle_login(self) -> bool:
        """
        檢查並處理登入

        Returns:
            bool: 是否成功登入
        """
        if self.browser.is_logged_in():
            self.logger.info("✅ 已登入 Facebook")
            return True

        else:
            self.logger.warning("⚠️  未登入 Facebook")
            self.logger.info("")
            self.logger.info("請在瀏覽器中手動登入 Facebook，然後按 Enter 繼續...")

            try:
                input()

                # 再次檢查
                if self.browser.is_logged_in():
                    self.logger.info("✅ 登入成功")

                    # 儲存 Cookies
                    self.browser.save_cookies(self.config.cookies_path)
                    self.logger.info(f"✅ Cookies 已儲存: {self.config.cookies_path}")

                    return True
                else:
                    self.logger.error("❌ 仍未登入，無法繼續")
                    return False

            except Exception as e:
                self.logger.error(f"登入處理失敗: {e}", exc_info=True)
                return False

    def _scraping_loop(self):
        """
        爬取主迴圈
        """
        max_posts = self.config.max_posts
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        no_new_content_count = 0

        self.logger.info(f"目標: 抓取 {max_posts} 則新貼文")
        self.logger.separator()

        while processed_count < max_posts and self.is_running:
            # 1. 提取當前頁面的貼文
            posts = self.extractor.extract_posts(self.browser.page)

            if not posts:
                self.logger.warning("未找到貼文元素，可能頁面未載入完成")
                time.sleep(2)
                continue

            self.logger.info(f"頁面上找到 {len(posts)} 個 article 元素")

            # 2. 處理每一則貼文
            for i, post_elem in enumerate(posts):
                if processed_count >= max_posts:
                    break

                if not self.is_running:
                    break

                try:
                    # 提取貼文資料
                    post_data = self.extractor.extract_post_data(post_elem)

                    if not post_data:
                        self.logger.debug(f"元素 {i+1}: 提取失敗或被過濾，跳過")
                        # 注意：這可能是留言、文本太短、或其他原因
                        continue

                    post_id = post_data['id']

                    # 檢查是否已處理過 (去重)
                    if self.state.is_processed(post_id):
                        self.logger.debug(f"貼文 {i+1}: {post_id} 已處理過，跳過")
                        self.state.mark_skipped(self.session_id)
                        skipped_count += 1
                        continue

                    # 儲存貼文
                    save_result = self.saver.save_post(post_data)

                    if save_result['success']:
                        # 標記為已處理
                        self.state.mark_processed(post_id, self.session_id)
                        processed_count += 1

                        # 顯示進度
                        self.logger.info(
                            f"✅ [{processed_count}/{max_posts}] "
                            f"{save_result['record_id']} | "
                            f"{post_data['text'][:50]}..."
                        )

                    else:
                        self.logger.error(f"❌ 儲存失敗: {save_result.get('error')}")
                        self.state.mark_failed(self.session_id)
                        failed_count += 1

                except Exception as e:
                    self.logger.error(f"處理貼文時出錯: {e}", exc_info=True)
                    self.state.mark_failed(self.session_id)
                    failed_count += 1

            # 3. 滾動載入更多
            if processed_count < max_posts and self.is_running:
                self.logger.info("滾動載入更多貼文...")

                has_new_content = self.browser.scroll_to_bottom()

                if not has_new_content:
                    no_new_content_count += 1
                    self.logger.warning(f"頁面沒有新內容 ({no_new_content_count}/3)")

                    if no_new_content_count >= 3:
                        self.logger.warning("連續 3 次沒有新內容，可能已到底部")
                        break
                else:
                    no_new_content_count = 0  # 重置計數

                # 等待新內容載入
                time.sleep(2)

        # 結束提示
        self.logger.separator()
        self.logger.info(f"本次爬取結束:")
        self.logger.info(f"  ✅ 成功: {processed_count} 則")
        self.logger.info(f"  ⏭️  跳過: {skipped_count} 則 (已存在)")
        self.logger.info(f"  ❌ 失敗: {failed_count} 則")
        self.logger.info(f"\n💡 提示: 檢查日誌中的 '跳過：這是留言' 訊息，了解過濾了多少留言")

    def _print_summary(self):
        """顯示執行摘要"""
        self.logger.separator('=')
        self.logger.info("執行摘要")
        self.logger.separator('=')

        # State 統計
        stats = self.state.get_stats()
        latest_session = stats.get('latest_session')

        if latest_session:
            self.logger.info(f"Session ID: {latest_session['session_id']}")
            self.logger.info(f"狀態: {latest_session['status']}")
            self.logger.info(f"本次處理: {latest_session['total_processed']} 則")
            self.logger.info(f"本次跳過: {latest_session['total_skipped']} 則")
            self.logger.info(f"本次失敗: {latest_session['total_failed']} 則")

        self.logger.info(f"歷史總計: {stats['total_all_time']} 則")

        # Saver 統計
        saver_stats = self.saver.get_stats()
        self.logger.info(f"資料檔案數: {saver_stats['total_files']}")
        self.logger.info(f"總貼文數: {saver_stats['total_posts']}")

        self.logger.separator('=')
        self.logger.info("感謝使用 Claude Scraper！")
        self.logger.separator('=')


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Facebook 租屋爬蟲')
    parser.add_argument(
        '--config',
        default='config/config.json',
        help='配置檔案路徑 (預設: config/config.json)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='使用無頭模式 (不顯示瀏覽器視窗)'
    )

    args = parser.parse_args()

    try:
        scraper = FacebookScraper(config_path=args.config)

        # 覆蓋 headless 設定
        if args.headless:
            scraper.config.data['scraper']['headless'] = True

        scraper.run()

    except FileNotFoundError as e:
        print(f"\n❌ 錯誤: {e}")
        print("\n請先建立配置檔案:")
        print("  cp config/config.example.json config/config.json")
        print("  然後編輯 config.json 填入您的社團 URL")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
