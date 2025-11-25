import React from 'react';
import { MapPin, Home, Calendar, ExternalLink } from 'lucide-react';

// ============================================
// 類型定義
// ============================================
interface Rental {
  id: string;
  notes: string;
  rent: string;
  district: string;
  housing_type: string;
  processed_date: string;
  url?: string;
}

// ============================================
// 配色系統 - 統一管理顏色
// ============================================
const COLORS = {
  primary: {
    blue: 'bg-blue-50 text-blue-700',
    purple: 'bg-purple-50 text-purple-700',
    gradient: 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
  },
  background: {
    page: 'bg-gradient-to-br from-gray-50 to-blue-50',
    card: 'bg-white',
    tag: 'bg-white'
  },
  text: {
    primary: 'text-gray-900',
    secondary: 'text-gray-600',
    muted: 'text-gray-500'
  },
  border: 'border-gray-100'
};

// ============================================
// 子元件 1: 標籤徽章
// ============================================
interface BadgeProps {
  icon: React.ReactNode;
  label: string;
  colorClass: string;
}

const Badge: React.FC<BadgeProps> = ({ icon, label, colorClass }) => (
  <span className={`inline-flex items-center gap-1 px-3 py-1 ${colorClass} rounded-full text-xs font-medium`}>
    {icon}
    {label}
  </span>
);

// ============================================
// 子元件 2: 租金顯示
// ============================================
interface RentDisplayProps {
  amount: string;
}

const RentDisplay: React.FC<RentDisplayProps> = ({ amount }) => (
  <div className="flex items-baseline gap-2">
    <span className={`text-3xl font-extrabold ${COLORS.text.primary}`}>
      ${amount}
    </span>
    <span className={`text-sm ${COLORS.text.muted}`}>/ 月</span>
  </div>
);

// ============================================
// 子元件 3: CTA 按鈕
// ============================================
interface CTAButtonProps {
  url?: string;
  label?: string;
}

const CTAButton: React.FC<CTAButtonProps> = ({ url, label = "查看詳情" }) => {
  if (!url) return null;
  
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`w-full mt-3 inline-flex items-center justify-center gap-2 px-4 py-3 ${COLORS.primary.gradient} text-white rounded-xl text-sm font-semibold transition-all duration-200 shadow-sm hover:shadow-md`}
    >
      {label}
      <ExternalLink size={16} />
    </a>
  );
};

// ============================================
// 主元件: 租屋卡片
// ============================================
interface RentalCardProps {
  rental: Rental;
}

const RentalCard: React.FC<RentalCardProps> = ({ rental }) => {
  return (
    <div className={`${COLORS.background.card} rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 border ${COLORS.border} flex flex-col h-full`}>
      {/* 標籤區域 */}
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <Badge 
          icon={<MapPin size={12} />}
          label={rental.district}
          colorClass={COLORS.primary.blue}
        />
        <Badge 
          icon={<Home size={12} />}
          label={rental.housing_type}
          colorClass={COLORS.primary.purple}
        />
      </div>

      {/* Notes - 最突出的內容 */}
      <h3 className={`${COLORS.text.primary} text-lg font-bold mb-4 leading-relaxed line-clamp-3 flex-grow`}>
        {rental.notes}
      </h3>

      {/* 底部資訊區 */}
      <div className="space-y-3 mt-auto">
        {/* 租金 */}
        <RentDisplay amount={rental.rent} />

        {/* 日期 */}
        <div className={`flex items-center gap-2 text-xs ${COLORS.text.muted}`}>
          <Calendar size={14} />
          <span>刊登時間：{rental.processed_date}</span>
        </div>

        {/* CTA 按鈕 */}
        <CTAButton url={rental.url} />
      </div>
    </div>
  );
};

// ============================================
// 頁面標題元件
// ============================================
const PageHeader: React.FC = () => (
  <div className="max-w-6xl mx-auto mb-8">
    <div className="text-center mb-6">
      <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-3">
        大台北租屋社團
        <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> 最新物件</span>
      </h1>
      <p className={`${COLORS.text.secondary} text-lg mb-2`}>每日更新 24 小時內最新物件</p>
      <p className={`text-sm ${COLORS.text.muted}`}>一次看完 FB 各大熱門租屋社團最新物件</p>
    </div>
  </div>
);

// ============================================
// 篩選標籤元件
// ============================================
const FilterTags: React.FC = () => {
  const tags = ['雅房', '分租套房', '獨立套房', '租金 $5,000～$20,000', '大台北地區'];
  
  return (
    <div className="max-w-6xl mx-auto mb-8">
      <div className="flex flex-wrap justify-center gap-2 text-sm">
        {tags.map((tag) => (
          <span 
            key={tag}
            className={`px-4 py-2 ${COLORS.background.tag} rounded-full ${COLORS.text.secondary} shadow-sm hover:shadow transition-shadow cursor-pointer`}
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
};

// ============================================
// 主頁面預覽
// ============================================
export default function RentalPreview() {
  // 模擬資料
  const sampleRentals: Rental[] = [
    {
      id: "2025-10-14-001",
      notes: "近捷運站，採光極佳，全新裝潢，可養寵物",
      rent: "15000",
      district: "大安區",
      housing_type: "雅房",
      processed_date: "2025-10-14",
      url: "https://facebook.com"
    },
    {
      id: "2025-10-14-002",
      notes: "獨立套房附陽台，家具家電全配，即可入住",
      rent: "18000",
      district: "中正區",
      housing_type: "套房",
      processed_date: "2025-10-14",
      url: "https://facebook.com"
    },
    {
      id: "2025-10-14-003",
      notes: "整層出租，四房兩廳，適合小家庭或合租",
      rent: "35000",
      district: "信義區",
      housing_type: "整層住家",
      processed_date: "2025-10-13",
      url: "https://facebook.com"
    }
  ];

  return (
    <div className={`min-h-screen ${COLORS.background.page} p-6`}>
      <PageHeader />
      <FilterTags />
      
      {/* 卡片網格 */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sampleRentals.map((rental) => (
          <RentalCard key={rental.id} rental={rental} />
        ))}
      </div>
    </div>
  );
}