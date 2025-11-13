"use client";

import React from 'react';
import { Zap, BarChart3, AlertTriangle } from 'lucide-react';

// ============================================
// TypeScript 類型定義
// ============================================
interface PageHeaderProps {
  totalListings?: number; // 物件總數（可選，預設會顯示示範數字）
}

// ============================================
// 配色系統 - 延續溫潤灰階
// ============================================
const COLORS = {
  text: {
    primary: '#2C2C2C',      // 主文字（極簡黑）
    secondary: '#6B6B6B',    // 次要文字
    muted: '#9B9B9B',        // 輔助文字
  },
  accent: {
    yellow: '#FCD34D',       // 金黃色背景
    yellowText: '#92400E',   // 金黃標籤文字
  }
};

// ============================================
// 主元件：頁面表頭
// ============================================
const PageHeader: React.FC<PageHeaderProps> = ({ totalListings = 156 }) => {
  return (
    <div className="w-full bg-gradient-to-br from-gray-50 to-blue-50 pb-6 pt-8 px-6">
      <div className="max-w-6xl mx-auto">

        {/* 主標題 - 極簡風格 */}
        <div className="text-center mb-4">
          <h1
            className="text-3xl sm:text-4xl font-bold"
            style={{ color: COLORS.text.primary }}
          >
            大台北 FB 租屋社團<br className="sm:hidden" />物件彙整
          </h1>
        </div>

        {/* 24小時標籤 */}
        <div className="flex justify-center mb-6">
          <div
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full"
            style={{
              backgroundColor: COLORS.accent.yellow,
              color: COLORS.accent.yellowText
            }}
          >
            <Zap size={18} strokeWidth={2.5} />
            <span className="font-semibold text-sm sm:text-base">24 小時內最新物件</span>
          </div>
        </div>

        {/* 價值主張區域 */}
        <div className="text-center mb-5">
          <div
            className="text-base sm:text-lg mb-1"
            style={{ color: COLORS.text.secondary }}
          >
            雅房 | 分租套房 | 獨立套房
          </div>
          <div
            className="text-lg sm:text-xl font-medium"
            style={{ color: COLORS.text.primary }}
          >
            $5K-$20K
          </div>
        </div>

        {/* 統計資訊區 */}
        <div className="flex flex-col items-center gap-2 mb-6">
          <div
            className="flex items-center gap-2 text-sm"
            style={{ color: COLORS.text.secondary }}
          >
            <Zap size={16} />
            <span>每日即時更新</span>
          </div>
          <div
            className="flex items-center gap-2 text-sm font-medium"
            style={{ color: COLORS.text.primary }}
          >
            <BarChart3 size={16} />
            <span>本日新增 {totalListings} 筆物件</span>
          </div>
        </div>

        {/* 資訊狀態圖例 */}
        <div className="flex flex-col items-center gap-2 pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2 text-xs sm:text-sm">
            <span className="w-3 h-3 rounded-full bg-gray-800"></span>
            <span style={{ color: COLORS.text.secondary }}>貼文提煉資訊</span>
          </div>
          <div className="flex items-center gap-2 text-xs sm:text-sm">
            <span className="w-3 h-3 rounded-full bg-gray-300"></span>
            <span style={{ color: COLORS.text.secondary }}>未提供</span>
          </div>
          <div className="flex items-center gap-2 text-xs sm:text-sm">
            <span className="w-3 h-3 rounded-full bg-orange-500"></span>
            <span className="flex items-center gap-1" style={{ color: COLORS.text.secondary }}>
              <AlertTriangle size={14} className="text-orange-500" />
              資訊衝突
            </span>
          </div>
        </div>

      </div>
    </div>
  );
};

export default PageHeader;
