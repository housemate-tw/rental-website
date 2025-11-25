# 解決方案設計：Claude Scraper 技術方案

**文件版本**: v1.0
**建立日期**: 2025-10-20
**負責 AI**: Claude (Sonnet 4.5)

---

## 1. 設計原則 (Design Principles)

### 1.1 核心原則

1. **穩定性優先** (Stability First)
   - 系統必須能連續運行數小時不崩潰
   - 所有可預見的錯誤都要處理

2. **可恢復性** (Recoverability)
   - 任何時刻中斷都能從上次位置繼續
   - 不重複處理已完成的貼文

3. **可觀測性** (Observability)
   - 任何時刻都能知道系統狀態
   - 所有錯誤都有完整日誌

4. **零 AI 依賴** (Zero AI Dependency)
   - 運行時不消耗 AI API Token
   - 不依賴 AI 對話來處理邏輯

5. **非破壞性整合** (Non-Destructive Integration)
   - 不修改 Gemini 的任何現有程式碼
   - 可隨時移除而不影響原系統

---

## 2. 技術方案選擇

### 2.1 方案比較

我們評估了三種可能的技術方案：

| 方案 | 優點 | 缺點 | 評分 |
|------|------|------|------|
| **A. Selenium** | 成熟穩定 | 效能較差、資源消耗高 | ⭐⭐⭐ |
| **B. Playwright** | 現代化、效能好、API 友善 | 相對較新 | ⭐⭐⭐⭐⭐ |
| **C. GraphQL API** | 最快速 | 需處理認證、易被偵測 | ⭐⭐⭐ |

**最終選擇**: **Playwright**

### 2.2 選擇 Playwright 的理由

#### 優勢

1. **現代化 API**
   ```python
   # Playwright 的 API 非常直觀
   page.goto(url)
   page.wait_for_selector('[role="article"]')
   posts = page.query_selector_all('[role="article"]')
   ```

2. **自動等待機制**
   - 內建智慧等待，減少 timeout 錯誤
   - 自動處理動態載入

3. **強大的選擇器**
   - 支援 CSS、XPath、Text、Role 等多種選擇器
   - 可處理 Shadow DOM

4. **截圖與除錯**
   - 錯誤時自動截圖
   - 可錄製操作過程

5. **效能優異**
   - 比 Selenium 快 20-30%
   - 記憶體佔用更少

#### 限制與應對

| 限制 | 應對措施 |
|------|----------|
| 需要下載瀏覽器 | 安裝腳本自動處理 |
| 學習曲線 | 提供完整範例程式碼 |
| 相容性問題 | 鎖定特定版本 |

---

## 3. 系統架構設計

### 3.1 整體架構

```
┌─────────────────────────────────────────────────────┐
│                  Claude Scraper                      │
│                                                      │
│  ┌──────────────┐      ┌──────────────┐            │
│  │   Scraper    │─────→│ State        │            │
│  │   Engine     │      │ Manager      │            │
│  └──────┬───────┘      └──────────────┘            │
│         │                                            │
│         │              ┌──────────────┐            │
│         └─────────────→│   Logger     │            │
│                        └──────────────┘            │
│                                                      │
│         ↓                                            │
│  ┌──────────────┐                                   │
│  │  Playwright  │                                   │
│  │   Browser    │                                   │
│  └──────┬───────┘                                   │
└─────────┼──────────────────────────────────────────┘
          │
          ↓
   ┌──────────────┐
   │  Facebook    │
   │   Website    │
   └──────┬───────┘
          │
          ↓
   ┌──────────────┐
   │  save_       │ (Gemini 的腳本)
   │  rental_     │
   │  v8.py       │
   └──────┬───────┘
          │
          ↓
   ┌──────────────┐
   │  data_v8/    │
   │  *.jsonl     │
   └──────────────┘
```

### 3.2 核心模組

#### 模組 1: Scraper Engine (`scraper.py`)

**職責**:
- 控制 Playwright 瀏覽器
- 滾動頁面載入貼文
- 提取貼文內容
- 去重處理

**核心流程**:
```python
1. 啟動瀏覽器並登入 Facebook
2. 導航到租屋社團
3. 進入爬取迴圈:
   3.1 滾動頁面
   3.2 等待貼文載入
   3.3 提取貼文內容
   3.4 檢查是否已處理（去重）
   3.5 呼叫 save_rental_v8.py 存檔
   3.6 更新狀態
   3.7 記錄日誌
4. 達到目標數量或使用者中斷時結束
```

#### 模組 2: State Manager (`state_manager.py`)

**職責**:
- 記錄已處理的貼文 ID
- 記錄當前滾動位置
- 提供斷點續傳能力

**資料結構**:
```json
{
  "last_run": "2025-10-20T18:30:00",
  "total_processed": 156,
  "processed_post_ids": [
    "post_id_1",
    "post_id_2",
    "..."
  ],
  "current_scroll_position": 3500,
  "session_id": "session_20251020_183000"
}
```

#### 模組 3: Logger (`logger.py`)

**職責**:
- 結構化日誌記錄
- 錯誤追蹤
- 效能監控

**日誌等級**:
```python
DEBUG   # 詳細的除錯資訊
INFO    # 一般執行資訊（成功處理貼文等）
WARNING # 警告但不影響執行（如重試）
ERROR   # 錯誤但程式繼續（如單一貼文解析失敗）
CRITICAL# 致命錯誤程式終止
```

#### 模組 4: Utils (`utils.py`)

**職責**:
- 文本清理
- 去重邏輯
- 配置載入
- 輔助函數

---

## 4. 關鍵技術決策

### 4.1 登入方式

**選項 A: 每次都登入**
- ❌ 觸發驗證碼風險高
- ❌ 速度慢

**選項 B: Cookie 持久化 (採用)**
- ✅ 第一次登入後儲存 Cookies
- ✅ 後續使用 Cookies 免登入
- ✅ 快速且穩定

**實作**:
```python
# 首次登入
context = browser.new_context()
page = context.new_page()
# ... 登入流程 ...
context.storage_state(path="auth.json")

# 後續使用
context = browser.new_context(storage_state="auth.json")
```

### 4.2 貼文載入策略

**問題**: Facebook 使用無限滾動，如何載入所有貼文？

**策略**:
```python
while True:
    # 1. 滾動到底部
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # 2. 等待新貼文載入
    time.sleep(2)  # 模擬真人瀏覽

    # 3. 檢查是否有新貼文
    new_count = page.query_selector_all('[role="article"]').length
    if new_count == old_count:
        # 沒有新貼文，可能已到底
        break

    # 4. 繼續滾動
    old_count = new_count
```

### 4.3 去重策略

**多層去重**:

1. **記憶體去重** (Session 內)
   ```python
   seen_ids = set()
   if post_id in seen_ids:
       continue
   seen_ids.add(post_id)
   ```

2. **狀態檔去重** (跨 Session)
   ```python
   state = StateManager.load()
   if post_id in state['processed_post_ids']:
       continue
   ```

3. **資料檔去重** (最終防線)
   - 讓 Gemini 的 `save_rental_v8.py` 處理
   - 使用內容指紋比對

### 4.4 錯誤處理策略

**錯誤分類與處理**:

| 錯誤類型 | 處理方式 | 重試次數 |
|----------|----------|----------|
| 網路 timeout | 自動重試 | 3 次 |
| 元素找不到 | 等待後重試 | 3 次 |
| Facebook 登出 | 重新載入 Cookies | 1 次 |
| Facebook 驗證碼 | 通知使用者，暫停 | 人工介入 |
| 磁碟空間不足 | 記錄錯誤，終止 | 0 次 |

**實作模式**:
```python
def retry_on_error(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError as e:
            logger.warning(f"Retry {attempt+1}/{max_retries}: {e}")
            time.sleep(2 ** attempt)  # 指數退避
        except FatalError as e:
            logger.error(f"Fatal error: {e}")
            raise
    raise MaxRetriesExceeded()
```

---

## 5. 整合 Gemini 系統

### 5.1 整合點：save_rental_v8.py

**Gemini 的腳本簽名**:
```python
python3 save_rental_v8.py \
    district \
    housing_type \
    rent \
    rent_range_json \
    is_multi_room \
    summary_notes \
    details_json \
    fees_json \
    room_details \
    raw_post \
    url
```

**Claude 的呼叫方式**:
```python
import subprocess
import json

def save_to_gemini_system(post_data):
    """呼叫 Gemini 的存檔腳本"""
    cmd = [
        'python3',
        '/Users/sabrina/Documents/rental_project/save_rental_v8.py',
        post_data['district'],
        post_data['housing_type'],
        post_data['rent'],
        json.dumps(post_data['rent_range']),
        str(post_data['is_multi_room']).lower(),
        post_data['summary_notes'],
        json.dumps(post_data['details']),
        json.dumps(post_data['fees']),
        post_data['room_details'],
        post_data['raw_post'],
        post_data['url']
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Save failed: {result.stderr}")

    return result.stdout
```

### 5.2 資料轉換

**問題**: Claude 抓取的原始貼文 vs Gemini 需要的結構化資料

**解決方案**:

**選項 A: Claude 自行結構化** (不推薦)
- ❌ 需要消耗 Claude API Token
- ❌ 重複 Gemini 已有的邏輯

**選項 B: 簡化版 save_rental.py** (採用)
- ✅ 只傳遞原始文本 + URL
- ✅ 讓 Gemini 負責結構化（維持原有分工）

**新建腳本**: `save_rental_raw.py` (Claude 新增)
```python
#!/usr/bin/env python3
"""
簡化版存檔腳本，只接收原始貼文
實際結構化處理仍呼叫 Gemini 的邏輯
"""
def save_raw_post(raw_text, url):
    # 1. 基本清理
    # 2. 呼叫 Gemini 的結構化邏輯（或 API）
    # 3. 呼叫 save_rental_v8.py
    pass
```

---

## 6. 效能與規模設計

### 6.1 效能目標

| 指標 | 目標值 | 測量方式 |
|------|--------|----------|
| 處理速度 | 10+ 貼文/分鐘 | 日誌統計 |
| 記憶體使用 | < 500MB | 系統監控 |
| CPU 使用 | < 50% | 系統監控 |
| 錯誤率 | < 5% | 日誌分析 |

### 6.2 規模限制

**單次執行**:
- 建議: 500 則貼文
- 最大: 2000 則貼文
- 原因: 避免被 Facebook 偵測為異常行為

**執行頻率**:
- 建議: 每天 1-2 次
- 間隔: 至少 6 小時
- 原因: 降低帳號風險

### 6.3 速度控制

**模擬真人行為**:
```python
# 滾動速度隨機化
scroll_delay = random.uniform(1.5, 3.0)

# 閱讀時間模擬
reading_delay = random.uniform(0.5, 1.5)

# 偶爾停頓
if random.random() < 0.1:  # 10% 機率
    time.sleep(random.uniform(5, 10))
```

---

## 7. 安全性與風險控制

### 7.1 帳號安全

**風險**:
- Facebook 偵測自動化行為並封鎖帳號

**緩解措施**:
1. **降低速度**: 每則貼文間隔 2-5 秒
2. **隨機化行為**: 滾動速度、停頓時間都加入隨機性
3. **限制數量**: 單次不超過 500 則
4. **使用者代理**: 使用真實的瀏覽器 User-Agent
5. **Cookie 管理**: 定期更新，避免過期

### 7.2 資料安全

**敏感資料**:
- Facebook 登入 Cookies
- 帳號密碼（如果有儲存）

**保護措施**:
```python
# 1. 配置檔不進版本控制
.gitignore:
    config/config.json
    config/auth.json

# 2. 加密儲存（選用）
from cryptography.fernet import Fernet
# 加密 auth.json
```

### 7.3 錯誤隔離

**原則**: 單一貼文的錯誤不應影響整體流程

```python
for post in posts:
    try:
        process_post(post)
    except Exception as e:
        logger.error(f"Failed to process post {post.id}: {e}")
        failed_posts.append(post.id)
        continue  # 繼續處理下一則
```

---

## 8. 可配置性設計

### 8.1 配置檔結構

**`config/config.json`**:
```json
{
  "facebook": {
    "group_url": "https://www.facebook.com/groups/...",
    "login_method": "cookies",
    "cookies_path": "config/auth.json"
  },
  "scraper": {
    "max_posts_per_run": 500,
    "scroll_delay": [1.5, 3.0],
    "reading_delay": [0.5, 1.5],
    "max_retries": 3
  },
  "paths": {
    "save_script": "/Users/sabrina/Documents/rental_project/save_rental_v8.py",
    "data_dir": "/Users/sabrina/Documents/data_v8",
    "state_file": "state/scraper_state.json",
    "log_dir": "logs/"
  }
}
```

### 8.2 環境變數支援

```python
import os

# 允許透過環境變數覆蓋配置
FB_GROUP_URL = os.getenv('FB_GROUP_URL') or config['facebook']['group_url']
MAX_POSTS = int(os.getenv('MAX_POSTS') or config['scraper']['max_posts_per_run'])
```

---

## 9. 監控與可觀測性

### 9.1 即時監控

**方式 A: 命令列輸出**
```
[2025-10-20 18:30:15] INFO: Scraper started
[2025-10-20 18:30:20] INFO: Logged in successfully
[2025-10-20 18:30:25] INFO: Processed post 1/500
[2025-10-20 18:30:30] INFO: Processed post 2/500
...
[2025-10-20 18:32:10] WARNING: Retrying post 15 (attempt 1/3)
[2025-10-20 18:32:15] INFO: Processed post 15/500
```

**方式 B: 進度條**
```python
from tqdm import tqdm

for post in tqdm(posts, desc="Processing posts"):
    process_post(post)
```

### 9.2 監控儀表板 (選用)

**簡易版**: `monitor.py`
```python
# 讀取日誌和狀態檔，顯示:
- 已處理貼文數
- 成功率
- 錯誤統計
- 預計完成時間
```

---

## 10. 擴展性考量

### 10.1 未來可能需求

1. **多社團支援**
   - 配置檔支援多個 group_url
   - 依序處理

2. **排程執行**
   - 整合 cron 或 systemd timer
   - 自動定時執行

3. **通知系統**
   - 完成時發送 Email/Slack 通知
   - 錯誤時警報

4. **資料分析**
   - 統計租金分布
   - 熱門地區分析

### 10.2 模組化設計

**原則**: 每個模組可獨立替換

```
scraper.py        → 可替換為其他爬蟲引擎
state_manager.py  → 可替換為 SQLite 或 Redis
logger.py         → 可替換為其他日誌系統
```

---

## 11. 成功標準

**此設計方案成功的標誌**:

1. ✅ 能夠產出完整的技術規格文件
2. ✅ 所有模組職責清晰、邊界明確
3. ✅ 錯誤處理策略完整
4. ✅ 與 Gemini 系統的整合點明確
5. ✅ 可配置、可擴展、可維護

---

**文件結束**

下一步請閱讀: `03_architecture.md`
