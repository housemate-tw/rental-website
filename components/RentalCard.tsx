"use client";

import React, { useState } from 'react';
import { MapPin, Home, FileCheck, ChevronDown, ChevronUp, Calendar, Coins, AlertTriangle } from 'lucide-react';

// ============================================
// TypeScript 類型定義
// ============================================
interface LayoutInfo {
  overall_layout?: string;
  room_size?: string;
  floor_info?: string;
}

interface RentalDetails {
  address: string | null;
  layout_info: LayoutInfo;
  rights: string;
}

interface RentalFees {
  electricity: string;        // 電費
  management?: string;        // 管理費（可選）
  cleaning?: string;          // 清潔費（可選）
  water?: string;             // 水費（可選）
  internet?: string;          // 網路費（可選）
  deposit: string;            // 押金
  included?: string;          // 其他包含費用（可選，向後兼容）
}

interface Rental {
  id: string;
  url?: string;
  district: string;
  housing_type: string;
  rent?: string;
  rent_range?: {
    min: string;
    max: string;
  };
  is_multi_room: boolean;
  posted_date: string;
  summary_notes: string;
  details: RentalDetails;
  room_details?: string;
  fees: RentalFees;
}

// ============================================
// 配色系統 - 溫潤灰階 + 警告色
// ============================================
const COLORS = {
  primary: '#4A4A4A',
  secondary: '#6B6B6B',
  light: '#D1D1D1',
  border: '#E5E5E5',
  background: '#FFFFFF',
  text: {
    primary: '#2C2C2C',
    secondary: '#6B6B6B',
    muted: '#9B9B9B',
    warning: '#D97706'
  }
};

// ============================================
// 子元件：標籤（底線式）
// ============================================
interface TagProps {
  children: React.ReactNode;
  emphasized?: boolean;
}

const Tag: React.FC<TagProps> = ({ children, emphasized = false }) => (
  <div className="inline-flex flex-col items-center">
    <span 
      className={`${emphasized ? 'text-lg font-bold' : 'text-sm font-medium'}`}
      style={{ color: COLORS.text.primary }}
    >
      {children}
    </span>
    <div 
      className="w-full h-0.5 mt-1"
      style={{ backgroundColor: emphasized ? COLORS.primary : COLORS.secondary }}
    />
  </div>
);

// ============================================
// 子元件：資訊列
// ============================================
interface InfoRowProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  valueStyle?: React.CSSProperties;
}

const InfoRow: React.FC<InfoRowProps> = ({ icon, label, value, valueStyle }) => (
  <div className="flex items-start gap-2 text-sm">
    <div className="flex items-center gap-1.5 min-w-[60px]" style={{ color: COLORS.text.secondary }}>
      {icon}
      <span className="font-medium">{label}</span>
    </div>
    <span style={{ color: COLORS.text.primary, ...valueStyle }}>{value}</span>
  </div>
);

// ============================================
// 子元件：格局資訊折疊區塊
// ============================================
interface LayoutInfoBlockProps {
  layoutInfo: LayoutInfo;
}

const LayoutInfoBlock: React.FC<LayoutInfoBlockProps> = ({ layoutInfo }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // 按優先級整理資訊：overall_layout > room_size > floor_info
  const layoutItems = [
    { label: '整屋格局', value: layoutInfo.overall_layout, key: 'overall_layout' },
    { label: '房間坪數', value: layoutInfo.room_size, key: 'room_size' },
    { label: '樓層', value: layoutInfo.floor_info, key: 'floor_info' },
  ].filter(item => item.value); // 只保留有值的項目

  // 如果沒有任何資訊，不顯示這個區塊
  if (layoutItems.length === 0) return null;

  // 只有1項：直接顯示，無收合按鈕
  if (layoutItems.length === 1) {
    return (
      <div className="mt-4">
        <div className="flex items-center gap-2 text-sm font-medium" style={{ color: COLORS.text.secondary }}>
          <Home size={16} />
          <span>格局說明</span>
        </div>
        <div className="mt-2 pl-6 text-sm" style={{ color: COLORS.text.secondary }}>
          {layoutItems[0].value}
        </div>
      </div>
    );
  }

  // 2項以上：顯示最重要的 + 收合按鈕
  return (
    <div className="mt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-sm font-medium hover:opacity-70 transition-opacity"
        style={{ color: COLORS.text.secondary }}
      >
        <Home size={16} />
        <span>格局說明</span>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {!isExpanded && (
        <div className="mt-2 pl-6 text-sm" style={{ color: COLORS.text.secondary }}>
          {layoutItems[0].value}
        </div>
      )}

      {isExpanded && (
        <div className="mt-2 pl-6 space-y-1 text-sm" style={{ color: COLORS.text.secondary }}>
          {layoutItems.map(item => (
            <div key={item.key}>{item.label}：{item.value}</div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// 子元件：費用折疊區塊
// ============================================
interface FeesBlockProps {
  fees: RentalFees;
}

const FeesBlock: React.FC<FeesBlockProps> = ({ fees }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // 將文字中的 ⚠️ 替換為向量圖標
  const renderTextWithWarningIcon = (text: string) => {
    if (!text.includes('⚠️')) return text;

    const parts = text.split('⚠️');
    return (
      <>
        {parts.map((part, index) => (
          <React.Fragment key={index}>
            {index > 0 && <AlertTriangle size={14} className="inline-block mx-1" />}
            {part}
          </React.Fragment>
        ))}
      </>
    );
  };

  // 按優先級整理費用項目：電費 > 管理費 > 清潔費 > 水費 > 網路費
  const allFeeItems = [
    { label: '電費', value: fees.electricity, key: 'electricity' },
    { label: '管理費', value: fees.management, key: 'management' },
    { label: '清潔費', value: fees.cleaning, key: 'cleaning' },
    { label: '水費', value: fees.water, key: 'water' },
    { label: '網路費', value: fees.internet, key: 'internet' },
  ];

  const feeItems = allFeeItems.filter(item => item.value !== undefined) as Array<{
    label: string;
    value: string;
    key: string;
  }>; // 只保留有值的項目

  // 檢查最重要的項目（第一個）是否有警告
  const topItemHasWarning = feeItems.length > 0 && feeItems[0].value.includes('⚠️');

  // 如果沒有任何費用項目，只顯示押金
  if (feeItems.length === 0) {
    return (
      <div className="mt-4">
        <div className="flex items-center gap-2 text-sm font-medium" style={{ color: COLORS.text.secondary }}>
          <Coins size={16} />
          <span>費用說明</span>
        </div>
        <div className="mt-2 pl-6 text-sm" style={{ color: COLORS.text.secondary }}>
          押金：{fees.deposit}
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-sm font-medium hover:opacity-70 transition-opacity"
        style={{ color: topItemHasWarning ? COLORS.text.warning : COLORS.text.secondary }}
      >
        <Coins size={16} />
        <span>費用說明</span>
        {topItemHasWarning && <AlertTriangle size={14} />}
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {/* 收合時：只顯示最重要的1項 */}
      {!isExpanded && (
        <div className="mt-1 pl-6 text-sm" style={{ color: topItemHasWarning ? COLORS.text.warning : COLORS.text.secondary }}>
          {feeItems[0].label}：{renderTextWithWarningIcon(feeItems[0].value)}
        </div>
      )}

      {/* 展開時：按優先級順序顯示所有項目 */}
      {isExpanded && (
        <div className="mt-2 pl-6 space-y-1 text-sm" style={{ color: COLORS.text.secondary }}>
          {feeItems.map(item => {
            const hasWarning = item.value.includes('⚠️');
            return (
              <div key={item.key} style={{ color: hasWarning ? COLORS.text.warning : COLORS.text.secondary }}>
                {item.label}：{renderTextWithWarningIcon(item.value)}
              </div>
            );
          })}
          <div>押金：{fees.deposit}</div>
          {fees.included && (
            <div>其他：{fees.included}</div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================
// 子元件：Notes 展開區塊
// ============================================
interface NotesBlockProps {
  notes: string;
}

const NotesBlock: React.FC<NotesBlockProps> = ({ notes }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const shouldTruncate = notes.length > 100;
  const hasWarning = notes.includes('⚠️');

  // 將文字中的 ⚠️ 替換為向量圖標，並智能分配顏色
  const renderNotesWithIcon = (text: string) => {
    if (!hasWarning) {
      return <span style={{ color: COLORS.text.primary }}>{text}</span>;
    }

    const warningIndex = text.indexOf('⚠️');
    if (warningIndex === -1) {
      return <span style={{ color: COLORS.text.primary }}>{text}</span>;
    }

    // 警告前的文字（如果有）
    const beforeWarning = text.substring(0, warningIndex);

    // 警告符號後的文字
    const afterWarningSymbol = text.substring(warningIndex + 2);

    // 找到第一個句號或逗號，標記警告訊息的結束
    const punctuationMatch = afterWarningSymbol.match(/[。，]/);

    let warningText = '';
    let normalText = '';

    if (punctuationMatch) {
      const punctuationIndex = punctuationMatch.index!;
      warningText = afterWarningSymbol.substring(0, punctuationIndex + 1);
      normalText = afterWarningSymbol.substring(punctuationIndex + 1);
    } else {
      // 找不到標點符號，整段視為警告
      warningText = afterWarningSymbol;
    }

    return (
      <>
        {beforeWarning && <span style={{ color: COLORS.text.primary }}>{beforeWarning}</span>}
        <span style={{ color: COLORS.text.warning }}>
          <AlertTriangle size={18} className="inline-block mr-1" />
          {warningText}
        </span>
        {normalText && <span style={{ color: COLORS.text.primary }}>{normalText}</span>}
      </>
    );
  };

  return (
    <div className="relative">
      <div
        className={`text-lg font-bold leading-relaxed ${!isExpanded && shouldTruncate ? 'line-clamp-3' : ''}`}
      >
        {renderNotesWithIcon(notes)}
      </div>

      {!isExpanded && shouldTruncate && (
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent" />
      )}

      {shouldTruncate && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2 text-sm font-medium hover:opacity-70 transition-opacity"
          style={{ color: COLORS.secondary }}
        >
          {isExpanded ? '收合' : '展開完整描述'}
        </button>
      )}
    </div>
  );
};

// ============================================
// 子元件：房型詳情展開區塊
// ============================================
interface RoomDetailsSectionProps {
  roomDetails: string;
}

const RoomDetailsSection: React.FC<RoomDetailsSectionProps> = ({ roomDetails }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const rooms = roomDetails.split('\n').filter(line => line.trim());
  
  if (rooms.length === 0) return null;
  
  return (
    <div className="mt-4 space-y-2">
      <div className="flex items-center gap-1.5 font-medium text-sm" style={{ color: COLORS.text.secondary }}>
        <Home size={16} />
        <span>房型詳情：</span>
      </div>
      <div className="pl-4 space-y-1 text-sm" style={{ color: COLORS.text.primary }}>
        {rooms.slice(0, isExpanded ? rooms.length : 3).map((room, index) => (
          <div key={index}>{room}</div>
        ))}
        
        {rooms.length > 3 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm font-medium hover:opacity-70 transition-opacity mt-2"
            style={{ color: COLORS.secondary }}
          >
            {isExpanded ? '收合 ▲' : `+ 查看另外 ${rooms.length - 3} 個房型 ▼`}
          </button>
        )}
      </div>
    </div>
  );
};

// ============================================
// 主元件：租屋卡片
// ============================================
interface RentalCardProps {
  rental: Rental;
}

const RentalCard: React.FC<RentalCardProps> = ({ rental }) => {
  const { 
    district, 
    housing_type, 
    rent, 
    rent_range,
    is_multi_room,
    summary_notes, 
    details, 
    room_details,
    fees, 
    posted_date, 
    url 
  } = rental;
  
  return (
    <div 
      className="rounded-xl p-6 transition-all duration-200 hover:shadow-md"
      style={{ 
        backgroundColor: COLORS.background,
        border: `1px solid ${COLORS.border}`
      }}
    >
      {/* 標籤區域 - 只有客觀資訊 */}
      <div className="flex items-end gap-6 mb-5">
        <Tag>{district}</Tag>
        <Tag>{housing_type}</Tag>
        {is_multi_room && rent_range ? (
          <Tag emphasized>${rent_range.min} - ${rent_range.max}</Tag>
        ) : (
          <Tag emphasized>${rent}</Tag>
        )}
      </div>

      {/* Notes 區域 - 包含警告 */}
      <NotesBlock notes={summary_notes} />

      {/* 分隔線 */}
      <div className="my-5" style={{ borderTop: `1px solid ${COLORS.light}` }} />

      {/* 詳細資訊 */}
      <div className="space-y-3">
        {/* 地址 */}
        {details.address !== null ? (
          <InfoRow 
            icon={<MapPin size={16} />}
            label="地址"
            value={details.address}
          />
        ) : (
          <InfoRow 
            icon={<MapPin size={16} />}
            label="地址"
            value="未提供"
            valueStyle={{ color: COLORS.text.muted }}
          />
        )}
        
        {/* 格局資訊 */}
        {(details.layout_info.room_size || details.layout_info.overall_layout || details.layout_info.floor_info) && (
          <LayoutInfoBlock layoutInfo={details.layout_info} />
        )}
        
        {/* 房型詳情（多房型專用）*/}
        {is_multi_room && room_details && (
          <RoomDetailsSection roomDetails={room_details} />
        )}
        
        {/* 權利 */}
        <InfoRow 
          icon={<FileCheck size={16} />}
          label="權利"
          value={details.rights}
          valueStyle={details.rights === "未說明" ? { color: COLORS.text.muted } : undefined}
        />
      </div>

      {/* 費用折疊區塊 */}
      <FeesBlock fees={fees} />

      {/* 刊登日期 */}
      <div 
        className="flex items-center gap-1 mt-4 text-xs"
        style={{ color: COLORS.text.muted }}
      >
        <Calendar size={12} />
        刊登於 {posted_date}
      </div>

      {/* CTA 連結 */}
      {url && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-5 block text-center text-sm font-medium hover:underline"
          style={{ color: '#334155' }}
        >
          查看完整物件資訊 →
        </a>
      )}
    </div>
  );
};

export default RentalCard;
