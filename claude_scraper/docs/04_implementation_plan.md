# 實作計劃：逐步開發指南

**文件版本**: v1.0
**建立日期**: 2025-10-20
**負責 AI**: Claude (Sonnet 4.5)

---

## 1. 實作策略

### 1.1 開發原則

1. **由簡入繁** (Simple to Complex)
   - 先建立最小可行版本 (MVP)
   - 逐步增加功能

2. **測試驅動** (Test as You Go)
   - 每個模組完成後立即測試
   - 不等全部完成才測試

3. **文檔同步** (Document as You Code)
   - 邊寫程式邊更新 `99_changelog.md`
   - 遇到問題更新 `06_troubleshooting.md`

4. **增量交付** (Incremental Delivery)
   - 每個階段都產出可運行的版本
   - 使用者可提早看到進展

---

## 2. 實作階段

### Phase 0: 環境準備 ✅

**目標**: 確保開發環境就緒

**步驟**:

```bash
# 1. 確認 Python 版本
python3 --version  # 需要 3.9+

# 2. 建立虛擬環境 (建議)
cd /Users/sabrina/Documents/housemate-finder-app/claude_scraper
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. 安裝依賴
pip install playwright python-dotenv tqdm

# 4. 安裝 Playwright 瀏覽器
playwright install chromium

# 5. 驗證 Gemini 腳本可執行
python3 /Users/sabrina/Documents/rental_project/save_rental_v8.py
```

**預期時間**: 10 分鐘

---

### Phase 1: 核心模組開發 🔨

#### 1.1 Logger System (優先度: 最高)

**為何先做**: 後續所有模組都需要日誌

**檔案**: `src/logger.py`

**實作內容**:

```python
import logging
import os
from datetime import datetime

class ScraperLogger:
    def __init__(self, log_dir='logs/'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # 建立 logger
        self.logger = logging.getLogger('scraper')
        self.logger.setLevel(logging.DEBUG)

        # 完整日誌
        today = datetime.now().strftime('%Y%m%d')
        fh_all = logging.FileHandler(
            f'{log_dir}/scraper_{today}.log',
            encoding='utf-8'
        )
        fh_all.setLevel(logging.DEBUG)

        # 錯誤日誌
        fh_error = logging.FileHandler(
            f'{log_dir}/error_{today}.log',
            encoding='utf-8'
        )
        fh_error.setLevel(logging.ERROR)

        # 格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s'
        )
        fh_all.setFormatter(formatter)
        fh_error.setFormatter(formatter)

        self.logger.addHandler(fh_all)
        self.logger.addHandler(fh_error)

        # Console handler (可選)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        self.logger.critical(message, exc_info=exc_info)
```

**測試**:

```python
# 測試腳本
logger = ScraperLogger('test_logs/')
logger.info("Test message")
logger.error("Test error")

# 檢查 test_logs/ 是否產生日誌檔
```

**完成標準**:
- ✅ 日誌檔正確產生
- ✅ 格式正確
- ✅ 錯誤日誌分離

**預期時間**: 30 分鐘

---

#### 1.2 State Manager

**檔案**: `src/state_manager.py`

**實作內容**:

```python
import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, state_file='state/scraper_state.json'):
        self.state_file = state_file
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        self.state = self._load_or_create()

    def _load_or_create(self):
        """載入或建立新狀態檔"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'version': '1.0',
                'sessions': [],
                'processed_post_ids': [],
                'metadata': {
                    'total_all_time': 0
                }
            }

    def save(self):
        """儲存狀態到檔案"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def start_session(self):
        """開始新 session"""
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'running',
            'total_processed': 0,
            'total_failed': 0
        }
        self.state['sessions'].append(session)
        self.save()
        return session_id

    def end_session(self, session_id, status='completed'):
        """結束 session"""
        for session in self.state['sessions']:
            if session['session_id'] == session_id:
                session['end_time'] = datetime.now().isoformat()
                session['status'] = status
                break
        self.save()

    def is_processed(self, post_id):
        """檢查是否已處理"""
        return post_id in [p['id'] for p in self.state['processed_post_ids']]

    def mark_processed(self, post_id, session_id):
        """標記為已處理"""
        if not self.is_processed(post_id):
            self.state['processed_post_ids'].append({
                'id': post_id,
                'processed_at': datetime.now().isoformat(),
                'session_id': session_id
            })
            self.state['metadata']['total_all_time'] += 1

            # 更新 session 統計
            for session in self.state['sessions']:
                if session['session_id'] == session_id:
                    session['total_processed'] += 1
                    break

            self.save()

    def increment_failed(self, session_id):
        """增加失敗計數"""
        for session in self.state['sessions']:
            if session['session_id'] == session_id:
                session['total_failed'] += 1
                break
        self.save()

    def get_stats(self):
        """取得統計資訊"""
        return {
            'total_all_time': self.state['metadata']['total_all_time'],
            'total_sessions': len(self.state['sessions']),
            'latest_session': self.state['sessions'][-1] if self.state['sessions'] else None
        }
```

**測試**:

```python
# 測試腳本
sm = StateManager('test_state/test.json')
session_id = sm.start_session()
sm.mark_processed('test_post_1', session_id)
assert sm.is_processed('test_post_1') == True
sm.end_session(session_id)
print(sm.get_stats())
```

**完成標準**:
- ✅ 狀態正確儲存和載入
- ✅ 去重邏輯正確
- ✅ 統計資訊正確

**預期時間**: 45 分鐘

---

#### 1.3 Configuration Loader

**檔案**: `src/config.py`

**實作內容**:

```python
import json
import os

class Config:
    def __init__(self, config_path='config/config.json'):
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file not found: {config_path}. "
                f"Please copy config.example.json to config.json"
            )

        with open(config_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def get(self, key_path, default=None):
        """
        取得配置值
        key_path 格式: 'facebook.group_url'
        """
        keys = key_path.split('.')
        value = self.data

        for key in keys:
            if key in value:
                value = value[key]
            else:
                return default

        return value

    # 便捷屬性
    @property
    def group_url(self):
        return self.get('facebook.group_url')

    @property
    def max_posts(self):
        return self.get('scraper.max_posts_per_run', 500)

    @property
    def save_script_path(self):
        return self.get('paths.save_script')

    # ... 其他常用配置
```

**預期時間**: 20 分鐘

---

### Phase 2: 瀏覽器控制 🌐

#### 2.1 基礎瀏覽器啟動

**檔案**: `src/browser.py`

**實作內容**:

```python
from playwright.sync_api import sync_playwright
import time
import random

class BrowserController:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self, headless=False):
        """啟動瀏覽器"""
        self.logger.info("Launching browser...")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        self.logger.info("Browser launched successfully")

    def create_context(self, cookies_path=None):
        """建立瀏覽器 context"""
        if cookies_path and os.path.exists(cookies_path):
            self.logger.info(f"Loading cookies from {cookies_path}")
            self.context = self.browser.new_context(
                storage_state=cookies_path,
                user_agent=self.config.get('facebook.user_agent'),
                viewport={'width': 1280, 'height': 720}
            )
        else:
            self.logger.info("Creating new context (no cookies)")
            self.context = self.browser.new_context(
                user_agent=self.config.get('facebook.user_agent'),
                viewport={'width': 1280, 'height': 720}
            )

        self.page = self.context.new_page()

    def save_cookies(self, path):
        """儲存 cookies"""
        self.logger.info(f"Saving cookies to {path}")
        self.context.storage_state(path=path)

    def goto(self, url, wait_until='networkidle'):
        """導航到網址"""
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until=wait_until)

    def scroll_to_bottom(self, delay=None):
        """滾動到底部"""
        if delay is None:
            delay = random.uniform(
                self.config.get('scraper.scroll_delay')[0],
                self.config.get('scraper.scroll_delay')[1]
            )

        old_height = self.page.evaluate("document.body.scrollHeight")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(delay)

        new_height = self.page.evaluate("document.body.scrollHeight")
        return new_height > old_height  # 是否有新內容

    def wait_for_selector(self, selector, timeout=30000):
        """等待元素出現"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Timeout waiting for {selector}: {e}")
            return False

    def close(self):
        """關閉瀏覽器"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Browser closed")
```

**測試**:

```python
# 手動測試
from src.browser import BrowserController
from src.config import Config
from src.logger import ScraperLogger

config = Config()
logger = ScraperLogger()
browser = BrowserController(config, logger)

browser.launch(headless=False)
browser.create_context()
browser.goto('https://www.facebook.com')

# 手動登入...
input("Press Enter after login...")

browser.save_cookies('config/auth.json')
browser.close()
```

**完成標準**:
- ✅ 瀏覽器成功啟動
- ✅ 可導航到 Facebook
- ✅ 可儲存和載入 Cookies

**預期時間**: 1 小時

---

#### 2.2 貼文提取

**檔案**: `src/extractor.py`

**實作內容**:

```python
class PostExtractor:
    def __init__(self, logger):
        self.logger = logger

    def extract_posts(self, page):
        """提取頁面上所有貼文"""
        posts = page.query_selector_all('[role="article"]')
        self.logger.info(f"Found {len(posts)} posts on page")
        return posts

    def extract_post_data(self, post_element):
        """從貼文元素提取資料"""
        try:
            # 提取貼文 ID (從 data-* 屬性或 URL)
            post_id = self._extract_post_id(post_element)

            # 提取文本內容
            text = self._extract_text(post_element)

            # 提取 URL
            url = self._extract_url(post_element)

            # 提取時間戳 (選用)
            timestamp = self._extract_timestamp(post_element)

            return {
                'id': post_id,
                'text': text,
                'url': url,
                'timestamp': timestamp
            }

        except Exception as e:
            self.logger.error(f"Failed to extract post data: {e}", exc_info=True)
            return None

    def _extract_post_id(self, element):
        """提取貼文 ID"""
        # 方法 1: 從 URL 提取
        link = element.query_selector('a[href*="/posts/"]')
        if link:
            href = link.get_attribute('href')
            # 解析 URL 取得 post ID
            import re
            match = re.search(r'/posts/(\d+)', href)
            if match:
                return match.group(1)

        # 方法 2: 從 data 屬性
        # ...

        # Fallback: 使用內容 hash
        import hashlib
        text = self._extract_text(element)
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def _extract_text(self, element):
        """提取貼文文本"""
        # 嘗試多種選擇器
        selectors = [
            '[data-ad-comet-preview="message"]',
            '[data-ad-preview="message"]',
            'div[dir="auto"]'
        ]

        for selector in selectors:
            text_elem = element.query_selector(selector)
            if text_elem:
                return text_elem.inner_text()

        return ""

    def _extract_url(self, element):
        """提取貼文 URL"""
        link = element.query_selector('a[href*="/posts/"], a[href*="permalink"]')
        if link:
            href = link.get_attribute('href')
            # 補全完整 URL
            if href.startswith('/'):
                return f"https://www.facebook.com{href}"
            return href
        return ""

    def _extract_timestamp(self, element):
        """提取時間戳 (選用)"""
        # ... 實作 ...
        return None
```

**測試**:

```python
# 在實際 Facebook 頁面測試
browser.goto(config.group_url)
extractor = PostExtractor(logger)
posts = extractor.extract_posts(browser.page)

if posts:
    data = extractor.extract_post_data(posts[0])
    print(data)
```

**完成標準**:
- ✅ 能提取貼文 ID
- ✅ 能提取貼文文本
- ✅ 能提取貼文 URL

**預期時間**: 1.5 小時

---

### Phase 3: 主程式整合 🔗

**檔案**: `src/scraper.py`

**實作內容**:

```python
from src.config import Config
from src.logger import ScraperLogger
from src.state_manager import StateManager
from src.browser import BrowserController
from src.extractor import PostExtractor
import subprocess
import time

class FacebookScraper:
    def __init__(self, config_path='config/config.json'):
        self.config = Config(config_path)
        self.logger = ScraperLogger(self.config.get('paths.log_dir'))
        self.state = StateManager(self.config.get('paths.state_file'))
        self.browser = BrowserController(self.config, self.logger)
        self.extractor = PostExtractor(self.logger)
        self.session_id = None

    def run(self):
        """主執行流程"""
        try:
            self.logger.info("=== Scraper Started ===")
            self.session_id = self.state.start_session()

            # 1. 啟動瀏覽器
            self.browser.launch(headless=self.config.get('scraper.headless', False))
            self.browser.create_context(self.config.get('facebook.cookies_path'))

            # 2. 導航到社團
            self.browser.goto(self.config.group_url)

            # 3. 檢查是否需要登入
            if not self._is_logged_in():
                self.logger.warning("Not logged in. Please login manually.")
                input("Press Enter after login...")
                self.browser.save_cookies(self.config.get('facebook.cookies_path'))

            # 4. 執行爬取
            self._scrape_loop()

            # 5. 結束
            self.state.end_session(self.session_id, 'completed')
            self.logger.info("=== Scraper Completed ===")

        except KeyboardInterrupt:
            self.logger.warning("Interrupted by user")
            self.state.end_session(self.session_id, 'interrupted')

        except Exception as e:
            self.logger.critical(f"Fatal error: {e}", exc_info=True)
            self.state.end_session(self.session_id, 'failed')

        finally:
            self.browser.close()
            self._print_summary()

    def _is_logged_in(self):
        """檢查是否已登入"""
        # 簡單檢查: 看是否有使用者選單
        return self.browser.page.query_selector('[aria-label*="Account"]') is not None

    def _scrape_loop(self):
        """爬取主迴圈"""
        max_posts = self.config.max_posts
        processed_count = 0

        while processed_count < max_posts:
            # 1. 提取當前頁面的貼文
            posts = self.extractor.extract_posts(self.browser.page)

            # 2. 處理每一則貼文
            for post_elem in posts:
                if processed_count >= max_posts:
                    break

                post_data = self.extractor.extract_post_data(post_elem)
                if not post_data:
                    continue

                # 3. 去重
                if self.state.is_processed(post_data['id']):
                    self.logger.debug(f"Skipping duplicate: {post_data['id']}")
                    continue

                # 4. 儲存
                if self._save_post(post_data):
                    self.state.mark_processed(post_data['id'], self.session_id)
                    processed_count += 1
                    self.logger.info(f"Processed {processed_count}/{max_posts}: {post_data['id']}")
                else:
                    self.state.increment_failed(self.session_id)

            # 5. 滾動載入更多
            has_more = self.browser.scroll_to_bottom()
            if not has_more:
                self.logger.info("Reached end of feed")
                break

            # 6. 等待新內容載入
            time.sleep(2)

    def _save_post(self, post_data):
        """儲存貼文 (呼叫 Gemini 腳本)"""
        try:
            # 簡化版: 直接傳遞原始文本
            # 實際使用時需根據 save_rental_v8.py 的參數調整

            cmd = [
                'python3',
                self.config.save_script_path,
                # ... 參數 (待實作) ...
                post_data['text'],
                post_data['url']
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.logger.debug(f"Saved: {result.stdout.strip()}")
                return True
            else:
                self.logger.error(f"Save failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Exception saving post: {e}", exc_info=True)
            return False

    def _print_summary(self):
        """印出執行摘要"""
        stats = self.state.get_stats()
        print("\n=== Summary ===")
        print(f"Total processed (this session): {stats['latest_session']['total_processed']}")
        print(f"Total failed (this session): {stats['latest_session']['total_failed']}")
        print(f"Total all time: {stats['total_all_time']}")


if __name__ == '__main__':
    scraper = FacebookScraper()
    scraper.run()
```

**完成標準**:
- ✅ 能完整執行爬取流程
- ✅ 去重正確
- ✅ 日誌和狀態正確記錄

**預期時間**: 2 小時

---

### Phase 4: 測試與優化 🧪

#### 4.1 整合測試

**測試項目**:

1. **小規模測試** (10 則貼文)
   ```bash
   # 修改 config.json: max_posts_per_run = 10
   python3 src/scraper.py
   ```

2. **中斷恢復測試**
   ```bash
   # 執行到一半按 Ctrl+C
   # 重新執行，檢查是否從上次位置繼續
   ```

3. **錯誤處理測試**
   - 斷網測試
   - 無效貼文測試
   - Cookies 過期測試

**預期時間**: 2 小時

#### 4.2 效能優化

**優化項目**:

1. **滾動速度調整**
   - 測試不同延遲是否影響成功率

2. **記憶體使用**
   - 監控長時間運行的記憶體

3. **日誌精簡**
   - 移除過於詳細的 DEBUG 日誌

**預期時間**: 1 小時

---

### Phase 5: 文檔完善 📝

#### 5.1 使用手冊

**建立**: `README.md`

```markdown
# Claude Scraper 快速開始

## 安裝

1. 安裝依賴:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. 設定配置:
   ```bash
   cp config/config.example.json config/config.json
   # 編輯 config.json
   ```

3. 首次登入:
   ```bash
   python3 src/scraper.py
   # 在瀏覽器中手動登入 Facebook
   ```

## 使用

```bash
python3 src/scraper.py
```

## 常見問題

見 `docs/06_troubleshooting.md`
```

#### 5.2 API 參考

**建立**: `docs/05_api_reference.md`

(列出所有類別和方法的詳細說明)

#### 5.3 故障排除

**建立**: `docs/06_troubleshooting.md`

(列出常見錯誤和解決方法)

#### 5.4 變更日誌

**建立**: `docs/99_changelog.md`

**預期時間**: 1.5 小時

---

## 3. 時程總覽

| Phase | 任務 | 預估時間 | 累計時間 |
|-------|------|----------|----------|
| 0 | 環境準備 | 10 min | 10 min |
| 1.1 | Logger | 30 min | 40 min |
| 1.2 | State Manager | 45 min | 1h 25m |
| 1.3 | Config | 20 min | 1h 45m |
| 2.1 | Browser | 1h | 2h 45m |
| 2.2 | Extractor | 1.5h | 4h 15m |
| 3 | Main Scraper | 2h | 6h 15m |
| 4.1 | Testing | 2h | 8h 15m |
| 4.2 | Optimization | 1h | 9h 15m |
| 5 | Documentation | 1.5h | 10h 45m |

**總計**: 約 11 小時 (分 2-3 天完成)

---

## 4. 檢查清單

### 開發完成檢查

- [ ] 所有模組通過單元測試
- [ ] 整合測試成功 (能抓取 100+ 則貼文)
- [ ] 錯誤處理完整 (模擬各種錯誤情境)
- [ ] 日誌清晰易讀
- [ ] 狀態檔正確更新
- [ ] 去重邏輯正確
- [ ] 與 Gemini 系統整合成功

### 文檔完成檢查

- [ ] README.md 完整
- [ ] 05_api_reference.md 完整
- [ ] 06_troubleshooting.md 包含常見問題
- [ ] 99_changelog.md 記錄所有變更
- [ ] 程式碼註解充足

### 交付檢查

- [ ] requirements.txt 正確
- [ ] .gitignore 正確
- [ ] config.example.json 提供
- [ ] 可在乾淨環境中安裝並運行
- [ ] 使用者可自行操作，無需 AI 協助

---

## 5. 風險應對

### 潛在問題與解決方案

| 問題 | 解決方案 |
|------|----------|
| Facebook UI 改版 | 使用多種選擇器，定期測試 |
| Playwright 不穩定 | 鎖定版本，充分測試 |
| 開發時間超出預期 | 先完成 MVP，進階功能後續再加 |
| 使用者環境問題 | 提供詳細的故障排除文檔 |

---

## 6. 下一步行動

### 立即開始

1. **確認環境準備完成**
   ```bash
   python3 --version
   pip install playwright python-dotenv tqdm
   playwright install chromium
   ```

2. **建立第一個模組: Logger**
   - 參考 Phase 1.1
   - 完成後測試

3. **逐步推進**
   - 每完成一個模組就測試
   - 更新 changelog

### 使用者參與點

在以下階段建議使用者參與測試:

1. **Phase 2.1 完成後**: 測試瀏覽器啟動和登入
2. **Phase 3 完成後**: 測試完整爬取流程 (10 則貼文)
3. **Phase 4.1 完成後**: 測試大規模爬取 (500 則貼文)

---

**文件結束**

開始實作前，請確認:
1. ✅ 已閱讀所有文檔 (00-04)
2. ✅ 理解整體架構
3. ✅ 環境準備就緒
4. ✅ 準備好時間投入 (2-3 天)

準備好了嗎？讓我們開始 Phase 0！
