# Facebook 租屋抓取專案開發日誌 (v2)

本文檔記錄了與 Gemini 合作，從零開始探索、設計並實現 Facebook 租屋貼文自動化抓取、結構化與存檔流程的完整歷程。

---

## 1. 專案目標 (Overall Goal)

自動化抓取公開 Facebook 社團中的租屋貼文，根據詳細的 PRD (v8.0) 規則進行結構化，最終產出可用於資料庫分析的 JSON 資料，並為這些資料打造一個現代化、適合手機瀏覽的網頁應用程式。

---

## 2. Gemini 的工作與成果 (My Contributions)

我負責整個專案的後端資料工程，確保資料的穩定流入與處理。以下是我完成的工作：

### 2.1 資料來源與抓取

*   **資料來源**: 公開的 Facebook 租屋社團。
*   **抓取方式**: 我不使用不穩定的 UI 模擬，而是直接呼叫 Facebook 內部的 **GraphQL API** (`https://www.facebook.com/api/graphql/`)。我透過 `curl` 指令，攜帶必要的參數與 `cursor` (用於分頁)，來獲取最原始、最完整的貼文資料。
*   **資料位置**: 所有成功抓取並結構化的租屋資料，都會以 **JSON Lines (`.jsonl`)** 格式，按日期存放在您的本地路徑：`/Users/sabrina/Documents/data_v8/`。

### 2.2 資料處理與結構化

*   **智慧提取**: 我的程式能自動識別一般貼文和「商品格式」貼文，並從各自不同的欄位中提取完整的內文、永久連結 (`permalink`) 和發布時間。
*   **全域歷史比對**: 在處理每篇新貼文時，我會為其內容產生一個「指紋」，並搜尋 `/data_v8/` 和 `/rental_rules/` 路徑下的**所有**歷史 `.jsonl` 檔案，以實現跨天、跨檔案的資料去重。
*   **安全存檔**: 我編寫並持續維護一個名為 `save_rental_v8.py` 的 Python 腳本。該腳本內建了「**檔案鎖 (File Lock)**」機制，確保在高併發處理下，每一筆資料都能獲得唯一且遞增的 ID，從根本上杜絕了資料寫入衝突的問題。

### 2.3 Web App 後端 API

*   **專案位置**: 我在 `/Users/sabrina/Documents/housemate-finder-app/` 路徑下，建立了一個 Next.js 專案。
*   **API 端點**: 我在專案中建立了一個 API Route (`/src/app/api/rentals/route.ts`)。當前端頁面訪問這個 API 時，它會**即時**讀取 `/data_v8/` 中的所有 `.jsonl` 檔案，將其合併、排序，並以 JSON 格式回傳。這意味著前端的資料永遠會和您本地的資料同步。

---

## 3. 給 Claude.ai 的協作指南 (Collaboration Guide for Claude.ai)

你好，Claude！我是 Gemini。我負責這個專案的後端資料流。為了讓我們能高效地協作，打造出最棒的前端體驗，請參考以下指南：

### 3.1 你的任務：UI/UX 設計與實現

你的核心任務是接管所有與「視覺」和「互動」相關的工作。使用者希望你能將現有的、功能性的但較為簡陋的介面，打造成一個精緻、美觀且符合現代審美的產品。

*   **專案技術棧**: `Next.js` / `React` / `TypeScript` / `Tailwind CSS`。
*   **工作目錄**: `/Users/sabrina/Documents/housemate-finder-app/`。
*   **主要修改目標**: 
    1.  `src/app/page.tsx` (主頁面佈局與標題)
    2.  `src/components/RentalCard.tsx` (核心的租屋資訊卡片)

### 3.2 如何獲取資料

你**不需要**自己處理資料的讀取或管理。我已經為你準備好了所有資料。

*   **API 端點**: 你只需要在前端頁面 (`page.tsx`) 中，透過 `fetch('/api/rentals')` 即可獲取所有租屋資料的 JSON 陣列。
*   **資料結構**: 每一筆資料的結構如下 (TypeScript interface)，你可以直接在你的元件中使用：
    ```typescript
    interface Rental {
      id: string;            // 唯一 ID (e.g., "2025-10-14-001")
      sequence: number;      // 當日序號
      notes: string;         // **【設計重點】** 使用者希望這個欄位最為突出
      rent: string;          // 租金
      district: string;      // 行政區
      housing_type: string;  // 房屋類型
      raw_post: string;      // 原始貼文內容 (備用)
      processed_date: string;// 處理日期 (e.g., "2025-10-14")
      url?: string;           // **【重要】** 原始貼文的 Facebook 連結
    }
    ```

### 3.3 設計重點與使用者回饋

*   **資訊層次**: 使用者明確指出，`notes` 應該是卡片上**最顯眼**的資訊。其次是 `district`、`housing_type` 和 `processed_date`。`rent` 的重要性可以降低。
*   **行動裝置優先**: 設計時請優先考慮手機上的瀏覽體驗。使用者提到目前的佈局在手機上需要左右滑動，這是不理想的。請確保最終設計是**垂直滾動**的響應式網格佈局。
*   **CTA (Call to Action)**: 每張卡片都需要一個清晰、易於點擊的按鈕（例如：「點擊查看詳情」），並使用 `url` 欄位連結到原始的 Facebook 貼文。

### 3.4 我們的協作方式

1.  我會確保 `/api/rentals` 端點永遠提供最新、最準確的資料。
2.  你可以專注於 `page.tsx` 和 `RentalCard.tsx` 的美化，盡情發揮你的設計才華。
3.  當你完成設計後，請提供修改後的程式碼，我會負責將其整合進專案中。

期待我們的合作！
