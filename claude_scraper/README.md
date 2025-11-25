# Claude Scraper - Facebook 租屋爬蟲系統

**版本**: v1.0
**狀態**: 規劃完成，待實作
**負責 AI**: Claude (Sonnet 4.5)

---

## 專案簡介

Claude Scraper 是一個穩定、可靠、可監控的 Facebook 租屋社團爬蟲系統，專為解決 Gemini 方案的穩定性問題而設計。

### 核心特點

- ✅ **零 AI Token 消耗**: 純程式化執行，不依賴 AI API
- ✅ **完整錯誤處理**: 自動重試、斷點續傳
- ✅ **狀態持久化**: 中斷後可從上次位置繼續
- ✅ **結構化日誌**: 所有操作都有完整記錄
- ✅ **非破壞性整合**: 與 Gemini 系統和平共存

---

## 快速開始

### 前置需求

- Python 3.9+
- macOS/Linux (Windows 未測試)
- 有效的 Facebook 帳號

### 安裝步驟

```bash
# 1. 進入專案目錄
cd /Users/sabrina/Documents/housemate-finder-app/claude_scraper

# 2. (建議) 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 安裝 Python 依賴
pip install -r requirements.txt

# 4. 安裝 Playwright 瀏覽器
playwright install chromium

# 5. 設定配置檔
cp config/config.example.json config/config.json
# 編輯 config.json，填入您的 Facebook 社團 URL
```

### 首次執行

```bash
# 執行爬蟲 (會開啟瀏覽器)
python3 src/scraper.py

# 第一次執行時:
# 1. 會開啟瀏覽器
# 2. 提示您手動登入 Facebook
# 3. 登入後按 Enter
# 4. 系統會自動儲存登入狀態 (Cookies)
# 5. 之後執行不需要再登入
```

### 後續執行

```bash
# 直接執行即可
python3 src/scraper.py

# 背景執行 (可選)
nohup python3 src/scraper.py > output.log 2>&1 &
```

---

## 文檔導覽

建議按順序閱讀：

1. **[00_project_overview.md](docs/00_project_overview.md)** - 專案總覽
2. **[01_problem_analysis.md](docs/01_problem_analysis.md)** - 問題分析
3. **[02_solution_design.md](docs/02_solution_design.md)** - 解決方案設計
4. **[03_architecture.md](docs/03_architecture.md)** - 系統架構
5. **[04_implementation_plan.md](docs/04_implementation_plan.md)** - 實作計劃

開發中或遇到問題時：

- **[05_api_reference.md](docs/05_api_reference.md)** - API 參考 (待完成)
- **[06_troubleshooting.md](docs/06_troubleshooting.md)** - 故障排除 (待完成)
- **[99_changelog.md](docs/99_changelog.md)** - 變更日誌 (待完成)

---

## 專案結構

```
claude_scraper/
├── docs/                   # 完整文檔
├── src/                    # 源碼 (待開發)
│   ├── scraper.py         # 主程式
│   ├── state_manager.py   # 狀態管理
│   ├── logger.py          # 日誌系統
│   └── ...
├── config/                 # 配置
│   ├── config.example.json
│   └── config.json (gitignore)
├── state/                  # 狀態檔案
├── logs/                   # 日誌
├── requirements.txt        # 依賴
└── README.md              # 本文件
```

---

## 配置說明

編輯 `config/config.json`:

```json
{
  "facebook": {
    "group_url": "https://www.facebook.com/groups/YOUR_GROUP_ID",
    ...
  },
  "scraper": {
    "max_posts_per_run": 500,  // 單次抓取數量
    ...
  }
}
```

完整配置說明見 `config/config.example.json`

---

## 常見問題

### Q: 執行時出現「瀏覽器未安裝」錯誤

```bash
playwright install chromium
```

### Q: 抓取到一半中斷了怎麼辦？

沒關係！再次執行 `python3 src/scraper.py`，系統會自動從上次位置繼續。

### Q: 如何查看執行日誌？

```bash
tail -f logs/scraper_YYYYMMDD.log
```

### Q: 如何重新開始 (清除所有進度)？

```bash
rm state/scraper_state.json
rm config/auth.json  # 如果要重新登入
```

更多問題見 `docs/06_troubleshooting.md`

---

## 與 Gemini 系統的關係

Claude Scraper 是**獨立的**爬蟲系統，但會：
- ✅ 呼叫 Gemini 的 `save_rental_v8.py` 存檔
- ✅ 資料存入相同的 `/data_v8/` 目錄
- ✅ 與 Gemini 的 Next.js App 共用資料

兩個系統**和平共存**，互不影響。

---

## 開發狀態

### 已完成 ✅

- [x] 完整的規劃文檔 (00-04)
- [x] 專案結構設計
- [x] 技術方案選擇

### 進行中 🔨

- [ ] 核心模組開發 (Phase 1-3)
- [ ] 測試與優化 (Phase 4)
- [ ] 文檔完善 (Phase 5)

### 預計完成時間

2-3 個工作天（約 11 小時純開發時間）

詳細進度見 `docs/04_implementation_plan.md`

---

## 授權與使用

本專案由 Claude (Anthropic) 為使用者 Aurelia 開發。

採用 Regret Minimization Framework 原則：
- 文檔優先於程式碼
- 可維護性優先於快速交付
- 獨立性優先於緊密整合

---

## 聯絡與支援

如果遇到問題：

1. 查看 `docs/06_troubleshooting.md`
2. 查看 `logs/` 中的錯誤日誌
3. 參考完整文檔 `docs/`

如需其他 AI 接手開發，從 `docs/00_project_overview.md` 開始閱讀。

---

**Ready to build something stable and reliable! 🚀**
