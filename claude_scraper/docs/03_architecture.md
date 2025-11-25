# 系統架構文件

**文件版本**: v1.0
**建立日期**: 2025-10-20
**負責 AI**: Claude (Sonnet 4.5)

---

## 1. 系統概覽

### 1.1 架構圖

```
┌────────────────────────────────────────────────────────────┐
│                      使用者                                 │
│          (執行 python3 src/scraper.py)                     │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ↓
┌────────────────────────────────────────────────────────────┐
│               Claude Scraper System                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Main Controller (scraper.py)                        │ │
│  │  - 初始化系統                                          │ │
│  │  - 協調各模組                                          │ │
│  │  - 主要執行迴圈                                        │ │
│  └─────┬───────────────────────────┬──────────────────────┘ │
│        │                           │                        │
│        ↓                           ↓                        │
│  ┌─────────────┐            ┌─────────────┐               │
│  │   State     │            │   Logger    │               │
│  │   Manager   │            │   System    │               │
│  │             │            │             │               │
│  │ - 進度追蹤   │            │ - 日誌記錄   │               │
│  │ - 去重管理   │            │ - 錯誤追蹤   │               │
│  │ - 狀態持久化 │            │ - 效能監控   │               │
│  └─────────────┘            └─────────────┘               │
│        │                                                    │
│        ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Browser Controller (Playwright)                     │ │
│  │  - 瀏覽器生命週期管理                                  │ │
│  │  - 登入與 Cookie 管理                                 │ │
│  │  - 頁面導航與滾動                                     │ │
│  └─────────────────────┬────────────────────────────────┘ │
│                        │                                  │
└────────────────────────┼──────────────────────────────────┘
                         │
                         ↓
              ┌──────────────────────┐
              │   Facebook Website    │
              │   (公開社團)           │
              └──────────┬────────────┘
                         │
     (抓取貼文原始內容)    │
                         ↓
              ┌──────────────────────┐
              │  Data Processing      │
              │  (呼叫 Gemini 腳本)   │
              └──────────┬────────────┘
                         │
                         ↓
              ┌──────────────────────┐
              │  save_rental_v8.py    │
              │  (Gemini 的存檔腳本)  │
              └──────────┬────────────┘
                         │
                         ↓
              ┌──────────────────────┐
              │  /data_v8/*.jsonl     │
              │  (結構化資料)         │
              └───────────────────────┘
```

---

## 2. 模組詳細設計

### 2.1 Main Controller (`src/scraper.py`)

#### 職責

主控制器，負責整個爬蟲流程的協調。

#### 核心函數

```python
class FacebookScraper:
    def __init__(self, config_path='config/config.json'):
        """初始化爬蟲"""

    def run(self):
        """主執行流程"""
        # 1. 載入配置
        # 2. 初始化瀏覽器
        # 3. 登入 Facebook
        # 4. 導航到社團
        # 5. 執行爬取迴圈
        # 6. 清理資源

    def _scrape_loop(self):
        """爬取主迴圈"""
        # 1. 滾動載入貼文
        # 2. 提取貼文元素
        # 3. 解析貼文內容
        # 4. 去重檢查
        # 5. 儲存資料
        # 6. 更新狀態

    def _extract_post_data(self, element):
        """從 DOM 元素提取貼文資料"""
        # 返回: { 'id', 'text', 'url', 'timestamp', ... }

    def _save_post(self, post_data):
        """儲存貼文 (呼叫 Gemini 腳本)"""
```

#### 執行流程

```
開始
  │
  ├→ 載入配置檔
  │
  ├→ 初始化 Playwright
  │    └→ 啟動瀏覽器 (Chromium)
  │
  ├→ 登入 Facebook
  │    ├→ 檢查是否有 Cookies
  │    ├→ 有 → 載入 Cookies
  │    └→ 無 → 提示使用者手動登入 → 儲存 Cookies
  │
  ├→ 導航到租屋社團
  │    └→ 等待頁面完全載入
  │
  ├→ 進入爬取迴圈
  │    │
  │    ├→ 滾動頁面
  │    │    └→ 等待新貼文載入
  │    │
  │    ├→ 抓取當前可見的所有貼文
  │    │
  │    ├→ 對每一則貼文:
  │    │    ├→ 提取 ID、內文、URL
  │    │    ├→ 檢查是否已處理 (去重)
  │    │    ├→ 若未處理:
  │    │    │    ├→ 呼叫 save_rental_v8.py
  │    │    │    ├→ 更新狀態檔
  │    │    │    └→ 記錄日誌
  │    │    └→ 若已處理:
  │    │         └→ 跳過
  │    │
  │    ├→ 檢查是否達到目標數量
  │    │    └→ 是 → 結束迴圈
  │    │
  │    └→ 否 → 繼續滾動
  │
  ├→ 關閉瀏覽器
  │
  └→ 產生執行報告
```

---

### 2.2 State Manager (`src/state_manager.py`)

#### 職責

管理爬蟲的狀態，實現斷點續傳和去重。

#### 資料結構

```python
# state/scraper_state.json
{
  "version": "1.0",
  "sessions": [
    {
      "session_id": "20251020_183000",
      "start_time": "2025-10-20T18:30:00",
      "end_time": "2025-10-20T19:45:00",
      "status": "completed",  # running, completed, failed
      "total_processed": 156,
      "total_failed": 3,
      "last_scroll_position": 4500
    }
  ],
  "processed_post_ids": [
    {
      "id": "facebook_post_id_1",
      "processed_at": "2025-10-20T18:31:00",
      "session_id": "20251020_183000"
    },
    ...
  ],
  "metadata": {
    "last_updated": "2025-10-20T19:45:00",
    "total_all_time": 312
  }
}
```

#### 核心函數

```python
class StateManager:
    def __init__(self, state_file='state/scraper_state.json'):
        """初始化狀態管理器"""

    def load_state(self):
        """載入狀態檔"""

    def save_state(self):
        """儲存狀態檔"""

    def is_processed(self, post_id):
        """檢查貼文是否已處理"""

    def mark_processed(self, post_id, session_id):
        """標記貼文為已處理"""

    def start_session(self):
        """開始新的爬取 session"""
        # 返回 session_id

    def end_session(self, session_id, status='completed'):
        """結束 session"""

    def get_stats(self):
        """取得統計資訊"""
        # 返回: { 'total', 'today', 'success_rate', ... }
```

#### 去重邏輯

```python
def is_duplicate(post_id):
    """多層去重檢查"""
    # 1. 記憶體快取 (最快)
    if post_id in memory_cache:
        return True

    # 2. 狀態檔 (較快)
    if state_manager.is_processed(post_id):
        return True

    # 3. 資料檔掃描 (最慢，fallback)
    if scan_data_files(post_id):
        return True

    return False
```

---

### 2.3 Logger System (`src/logger.py`)

#### 職責

提供結構化日誌記錄，便於除錯和監控。

#### 日誌架構

```
logs/
├── scraper_20251020.log        # 當日完整日誌
├── error_20251020.log          # 當日錯誤日誌
└── archive/                    # 歷史日誌
    ├── scraper_20251019.log
    └── error_20251019.log
```

#### 日誌格式

```
[2025-10-20 18:30:15.123] [INFO] [scraper] Scraper started with config: config/config.json
[2025-10-20 18:30:20.456] [INFO] [browser] Browser launched successfully
[2025-10-20 18:30:25.789] [INFO] [auth] Logged in using cookies
[2025-10-20 18:30:30.012] [INFO] [scraper] Navigated to group: https://...
[2025-10-20 18:30:35.345] [INFO] [processor] Processed post 1/500: ID=post_123
[2025-10-20 18:30:40.678] [WARNING] [processor] Retry 1/3 for post_456: Timeout
[2025-10-20 18:30:45.901] [ERROR] [saver] Failed to save post_789: Invalid data
[2025-10-20 18:30:50.234] [CRITICAL] [scraper] Fatal error: Out of memory
```

#### 核心函數

```python
class ScraperLogger:
    def __init__(self, log_dir='logs/'):
        """初始化日誌系統"""
        # 設定兩個 handler:
        # 1. FileHandler → 所有日誌
        # 2. FileHandler → 只記錄 ERROR 以上

    def info(self, module, message):
        """記錄一般資訊"""

    def warning(self, module, message):
        """記錄警告"""

    def error(self, module, message, exc_info=None):
        """記錄錯誤"""

    def critical(self, module, message, exc_info=None):
        """記錄致命錯誤"""

    def performance(self, metric_name, value):
        """記錄效能指標"""
        # 例如: 每分鐘處理貼文數

    def get_session_summary(self, session_id):
        """取得 session 的日誌摘要"""
        # 分析日誌檔，返回統計
```

---

### 2.4 Browser Controller (整合在 `scraper.py`)

#### 職責

管理 Playwright 瀏覽器的生命週期和操作。

#### 核心函數

```python
class BrowserController:
    def __init__(self, config):
        """初始化瀏覽器控制器"""
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self, headless=False):
        """啟動瀏覽器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)

    def login(self, cookies_path=None):
        """登入 Facebook"""
        if cookies_path and os.path.exists(cookies_path):
            # 使用 Cookies 登入
            self.context = self.browser.new_context(
                storage_state=cookies_path
            )
        else:
            # 提示使用者手動登入
            self.context = self.browser.new_context()
            # ... 等待使用者登入 ...
            # 儲存 Cookies
            self.context.storage_state(path=cookies_path)

    def navigate_to_group(self, group_url):
        """導航到社團"""
        self.page = self.context.new_page()
        self.page.goto(group_url)
        self.page.wait_for_load_state('networkidle')

    def scroll_and_load(self):
        """滾動頁面載入更多貼文"""
        old_height = self.page.evaluate("document.body.scrollHeight")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(random.uniform(2, 4))  # 模擬真人

        # 等待新內容載入
        self.page.wait_for_timeout(1000)

        new_height = self.page.evaluate("document.body.scrollHeight")
        return new_height > old_height  # 返回是否有新內容

    def extract_posts(self):
        """提取當前頁面的所有貼文元素"""
        return self.page.query_selector_all('[role="article"]')

    def extract_post_data(self, post_element):
        """從貼文元素提取資料"""
        # 提取文本、URL、時間戳等

    def close(self):
        """關閉瀏覽器"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
```

---

## 3. 資料流程

### 3.1 完整資料流

```
Facebook 貼文 (HTML)
    ↓
[extract_post_data]
    ↓
原始資料 Dict:
{
  'id': 'facebook_post_12345',
  'text': '【板橋車站騎車6分鐘｜採光大雅房...',
  'url': 'https://www.facebook.com/...',
  'timestamp': '2025-10-20T18:30:00',
  'author': 'John Doe'
}
    ↓
[is_duplicate]
    ↓
未處理 → 繼續
已處理 → 跳過
    ↓
[呼叫 save_rental_v8.py]
輸入: raw_text, url
    ↓
[Gemini 的結構化處理]
    ↓
結構化資料:
{
  'id': '2025-10-20-157',
  'district': '板橋區',
  'rent': '11900',
  'housing_type': '雅房',
  'notes': '...',
  ...
}
    ↓
[存入 data_v8/2025-10-20.jsonl]
    ↓
[更新 state/scraper_state.json]
    ↓
[記錄 logs/scraper_20251020.log]
```

### 3.2 錯誤處理流

```
執行動作
    ↓
是否成功?
    ├→ 是 → 繼續
    └→ 否 → 錯誤類型?
            ├→ 網路 Timeout
            │    ↓
            │  重試次數 < 3?
            │    ├→ 是 → 等待 2^n 秒 → 重試
            │    └→ 否 → 記錄錯誤 → 跳過此貼文
            │
            ├→ 元素找不到
            │    ↓
            │  等待 5 秒 → 重試 → 失敗 → 記錄 → 跳過
            │
            ├→ Facebook 驗證碼
            │    ↓
            │  通知使用者 → 暫停程式 → 等待人工介入
            │
            └→ 其他錯誤
                 ↓
               記錄完整 traceback → 跳過此貼文
```

---

## 4. 檔案結構

```
claude_scraper/
├── docs/                          # 文檔目錄
│   ├── 00_project_overview.md
│   ├── 01_problem_analysis.md
│   ├── 02_solution_design.md
│   ├── 03_architecture.md         # 本文件
│   ├── 04_implementation_plan.md
│   ├── 05_api_reference.md
│   ├── 06_troubleshooting.md
│   └── 99_changelog.md
│
├── src/                           # 源碼目錄
│   ├── __init__.py
│   ├── scraper.py                 # 主程式
│   ├── state_manager.py           # 狀態管理
│   ├── logger.py                  # 日誌系統
│   └── utils.py                   # 工具函數
│
├── config/                        # 配置目錄
│   ├── config.example.json        # 配置範例
│   ├── config.json                # 實際配置 (gitignore)
│   └── auth.json                  # Cookies (gitignore)
│
├── state/                         # 狀態目錄
│   └── scraper_state.json         # 爬蟲狀態
│
├── logs/                          # 日誌目錄
│   ├── scraper_YYYYMMDD.log
│   ├── error_YYYYMMDD.log
│   └── archive/
│
├── tests/                         # 測試目錄
│   ├── test_scraper.py
│   ├── test_state_manager.py
│   └── test_logger.py
│
├── requirements.txt               # Python 依賴
├── .gitignore                     # Git 忽略檔案
└── README.md                      # 快速開始
```

---

## 5. 依賴關係

### 5.1 Python 套件

```txt
# requirements.txt
playwright==1.40.0          # 瀏覽器自動化
python-dotenv==1.0.0        # 環境變數管理
tqdm==4.66.1                # 進度條
```

### 5.2 外部依賴

- Playwright 瀏覽器 (Chromium)
  - 安裝: `playwright install chromium`
  - 大小: ~300MB

- Gemini 的 `save_rental_v8.py`
  - 路徑: `/Users/sabrina/Documents/rental_project/save_rental_v8.py`
  - 必須可執行

---

## 6. 配置管理

### 6.1 配置檔範例

```json
{
  "facebook": {
    "group_url": "https://www.facebook.com/groups/YOUR_GROUP_ID",
    "login_method": "cookies",
    "cookies_path": "config/auth.json",
    "user_agent": "Mozilla/5.0 ..."
  },
  "scraper": {
    "max_posts_per_run": 500,
    "scroll_delay": [1.5, 3.0],
    "reading_delay": [0.5, 1.5],
    "max_retries": 3,
    "retry_delay": 2,
    "headless": false
  },
  "paths": {
    "save_script": "/Users/sabrina/Documents/rental_project/save_rental_v8.py",
    "data_dir": "/Users/sabrina/Documents/data_v8",
    "state_file": "state/scraper_state.json",
    "log_dir": "logs/"
  },
  "monitoring": {
    "enable_progress_bar": true,
    "log_level": "INFO",
    "performance_tracking": true
  }
}
```

---

## 7. 安全性設計

### 7.1 敏感資料保護

```python
# .gitignore
config/config.json
config/auth.json
logs/*.log
state/scraper_state.json
*.pyc
__pycache__/
```

### 7.2 錯誤資訊脫敏

```python
# 日誌中不記錄敏感資訊
logger.info(f"Logged in as user: ***@***.com")  # 脫敏
logger.error(f"Failed to access URL: {url[:50]}...")  # 截斷
```

---

## 8. 效能考量

### 8.1 記憶體管理

```python
# 避免一次載入所有貼文到記憶體
# 使用串流處理

for post in stream_posts():  # Generator
    process(post)
    # 處理完即釋放
```

### 8.2 磁碟 I/O 優化

```python
# 狀態檔批次更新
state_manager.batch_mark_processed(post_ids)  # 批次寫入
# 而非每次都寫檔
```

---

## 9. 可測試性

### 9.1 模組獨立性

每個模組都可獨立測試：

```python
# 測試 State Manager
def test_state_manager():
    sm = StateManager('test_state.json')
    sm.mark_processed('test_id')
    assert sm.is_processed('test_id') == True

# 測試 Logger
def test_logger():
    logger = ScraperLogger('test_logs/')
    logger.info('test', 'Test message')
    # 檢查日誌檔內容
```

### 9.2 Mock 外部依賴

```python
# 測試時 Mock Playwright
@patch('playwright.sync_api.sync_playwright')
def test_scraper(mock_playwright):
    # 不實際啟動瀏覽器
    pass
```

---

## 10. 擴展點

### 10.1 未來可擴展的部分

1. **多社團支援**
   - `scraper.py` 支援傳入社團列表
   - 依序處理每個社團

2. **分散式爬蟲**
   - 使用 Redis 作為共享狀態儲存
   - 多台機器同時爬取

3. **即時通知**
   - 整合 Webhook
   - 完成時發送通知

---

**文件結束**

下一步請閱讀: `04_implementation_plan.md`
