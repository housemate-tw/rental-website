# Claude Scraper - 快速開始指南

## 🎯 5 分鐘快速上手

### 步驟 1: 檢查 Python 版本

```bash
python3 --version  # 需要 3.9+
```

### 步驟 2: 進入專案目錄

```bash
cd /Users/sabrina/Documents/housemate-finder-app/claude_scraper
```

### 步驟 3: 安裝依賴

```bash
# 安裝 Python 套件
pip3 install playwright python-dotenv tqdm

# 安裝 Playwright 瀏覽器
playwright install chromium
```

### 步驟 4: 設定配置檔

```bash
# 編輯配置檔
nano config/config.json

# 或使用 VSCode
code config/config.json
```

**重要**: 將 `YOUR_GROUP_ID` 替換為實際的 Facebook 社團 ID

例如：
```json
{
  "facebook": {
    "group_url": "https://www.facebook.com/groups/592050261354334",
    ...
  }
}
```

### 步驟 5: 首次執行

```bash
python3 src/scraper.py
```

**會發生什麼**:
1. 瀏覽器會自動開啟
2. 導航到 Facebook
3. 提示您手動登入
4. 登入後按 Enter
5. 系統會自動儲存登入狀態
6. 開始抓取貼文

### 步驟 6: 後續執行

```bash
# 直接執行即可 (不需要再登入)
python3 src/scraper.py

# 使用無頭模式 (不顯示瀏覽器)
python3 src/scraper.py --headless
```

---

## 📁 檔案位置

執行後會自動建立以下目錄和檔案：

```
claude_scraper/
├── config/
│   ├── config.json          # 配置檔
│   └── auth.json            # 登入狀態 (自動產生)
├── data/
│   └── YYYY-MM-DD_raw_posts.jsonl  # 抓取的貼文
├── state/
│   └── scraper_state.json   # 執行狀態 (去重)
└── logs/
    ├── scraper_YYYYMMDD.log # 完整日誌
    └── error_YYYYMMDD.log   # 錯誤日誌
```

---

## 🔍 查看結果

### 查看今天抓取的貼文

```bash
# 方法 1: 直接查看檔案
cat data/$(date +%Y-%m-%d)_raw_posts.jsonl

# 方法 2: 格式化顯示
python3 -c "
import json
from datetime import datetime

date = datetime.now().strftime('%Y-%m-%d')
filepath = f'data/{date}_raw_posts.jsonl'

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            print(f\"\n[{i}] {data['record_id']}\")
            print(f\"  文本: {data['text'][:100]}...\")
            print(f\"  URL: {data['url']}\")
except FileNotFoundError:
    print('今天還沒有抓取資料')
"
```

### 查看日誌

```bash
# 即時查看日誌
tail -f logs/scraper_$(date +%Y%m%d).log

# 查看錯誤日誌
cat logs/error_$(date +%Y%m%d).log
```

### 查看統計

```bash
# 查看狀態檔
cat state/scraper_state.json | python3 -m json.tool
```

---

## ⚙️ 配置調整

### 調整抓取數量

編輯 `config/config.json`:

```json
{
  "scraper": {
    "max_posts_per_run": 10,  // 改為 10 則 (測試用)
    ...
  }
}
```

### 更換目標社團

```json
{
  "facebook": {
    "group_url": "https://www.facebook.com/groups/NEW_GROUP_ID",
    ...
  }
}
```

### 使用無頭模式

```json
{
  "scraper": {
    "headless": true,  // 改為 true
    ...
  }
}
```

---

## 🐛 常見問題

### 問題 1: 提示「配置檔案不存在」

```bash
# 複製範例配置
cp config/config.example.json config/config.json
```

### 問題 2: 提示「playwright 未安裝」

```bash
playwright install chromium
```

### 問題 3: Cookies 過期

```bash
# 刪除舊的 Cookies
rm config/auth.json

# 重新執行，會提示您重新登入
python3 src/scraper.py
```

### 問題 4: 想重新開始 (清除所有進度)

```bash
# 清除狀態 (會重新抓取所有貼文)
rm state/scraper_state.json

# 清除登入狀態 (需要重新登入)
rm config/auth.json
```

---

## 📊 進階使用

### 背景執行

```bash
# 方法 1: 使用 nohup
nohup python3 src/scraper.py > output.log 2>&1 &

# 查看進程
ps aux | grep scraper

# 查看輸出
tail -f output.log

# 方法 2: 使用 screen
screen -S scraper
python3 src/scraper.py
# 按 Ctrl+A, D 離開
# 重新連接: screen -r scraper
```

### 定時執行 (cron)

```bash
# 編輯 crontab
crontab -e

# 每天早上 9:00 執行
0 9 * * * cd /Users/sabrina/Documents/housemate-finder-app/claude_scraper && python3 src/scraper.py >> cron.log 2>&1
```

---

## 💡 提示

1. **首次執行建議**: 先設定 `max_posts_per_run: 10` 測試
2. **登入狀態**: Cookies 通常有效 30 天
3. **去重機制**: 自動跳過已抓取的貼文
4. **中斷恢復**: 按 Ctrl+C 安全中斷，下次執行會從斷點繼續
5. **日誌追蹤**: 遇到問題先查看 `logs/error_*.log`

---

## 🎉 測試成功的標誌

執行成功後，您應該看到：

```
✅ [1/10] 2025-10-22-001 | 租金15000, 捷運站旁...
✅ [2/10] 2025-10-22-002 | 整層住家出租, 近大學...
...
✅ 爬取完成
```

並且在 `data/` 目錄下會有今天的 JSONL 檔案。

---

需要協助？查看 `docs/` 目錄中的完整文檔！
