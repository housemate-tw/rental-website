# Facebook 反爬蟲應對策略

## 問題

Facebook 會檢測自動化瀏覽器，導致：
- ❌ 反覆要求登入
- ❌ 機器人驗證（CAPTCHA）
- ❌ "Something went wrong" 錯誤

## 解決方案

### 1. 清除舊的 Cookies（重要！）

舊的 cookies 可能已被 Facebook 標記為可疑。

```bash
# 刪除舊的 cookies
rm config/auth.json

# 刪除 state 檔案
rm -rf state/

# 重新運行，這次會要求手動登入
python3 src/scraper.py
```

### 2. 降低爬取頻率

修改 `config/config.json`：

```json
{
  "scraper": {
    "max_posts_per_run": 5,        // 從 10 降到 5
    "scroll_delay": [3.0, 5.0],    // 增加延遲
    "reading_delay": [1.5, 3.0],   // 增加延遲
    ...
  }
}
```

### 3. 減少運行次數

**不要頻繁執行**：
- ❌ 不要連續執行多次
- ❌ 不要短時間內抓太多資料
- ✅ 每次執行後等待至少 10-15 分鐘
- ✅ 一天最多執行 3-5 次

### 4. 使用真實瀏覽器的 Profile（推薦）

這是最安全的方法，但需要額外配置。

### 5. 手動操作 + 部分自動化

如果自動化持續失敗，考慮：
1. 手動在瀏覽器中打開社團
2. 手動滾動到看到貼文
3. 使用腳本提取已載入的內容

## 當前改進

我已經添加了以下反檢測措施：

✅ 移除 `navigator.webdriver` 標記
✅ 偽造 `window.chrome` 物件
✅ 修改 `navigator.plugins`
✅ 設定正確的語言
✅ 增加更多瀏覽器參數

## 測試步驟

1. **清除 cookies**
2. **重新登入**
3. **只抓 5 則貼文測試**
4. **觀察是否觸發檢測**

## 如果還是失敗

考慮：
1. **使用 Facebook Graph API**（需要申請）
2. **手動複製貼文資料**
3. **使用第三方租屋平台** (591, 樂屋網等)
4. **增加更長的延遲** (每次操作等 5-10 秒)
