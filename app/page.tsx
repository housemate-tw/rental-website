import React from 'react';
import RentalCard from '@/components/RentalCard';
import PageHeader from '@/components/PageHeader';

// 示範資料
const sampleRentals = [
  {
    id: "2025-10-14-001",
    district: "大安區",
    housing_type: "雅房",
    rent: "15000",
    is_multi_room: false,
    posted_date: "2025-10-14",
    summary_notes: "近捷運站，採光極佳，全新裝潢，可養寵物",
    details: {
      address: "台北市大安區信義路四段XX號",
      layout_info: {
        room_size: "8坪",
        overall_layout: "3房2廳",
        floor_info: "5樓"
      },
      rights: "可租補、可入籍"
    },
    fees: {
      electricity: "依台電費率",
      deposit: "2個月",
      included: "水費、網路費、管理費"
    },
    url: "https://facebook.com"
  },
  {
    id: "2025-10-14-002",
    district: "中正區",
    housing_type: "套房",
    rent: "18000",
    is_multi_room: false,
    posted_date: "2025-10-14",
    summary_notes: "獨立套房附陽台，家具家電全配，即可入住",
    details: {
      address: null,
      layout_info: {
        room_size: "10坪"
      },
      rights: "未說明"
    },
    fees: {
      electricity: "每度5元",
      deposit: "1個月",
      included: "管理費"
    },
    url: "https://facebook.com"
  },
  {
    id: "2025-10-14-003",
    district: "信義區",
    housing_type: "共生宅",
    rent_range: {
      min: "11800",
      max: "12300"
    },
    is_multi_room: true,
    posted_date: "2025-10-13",
    summary_notes: "⚠️ 電費標示衝突。近101商圈，交通便利，生活機能完善",
    details: {
      address: "台北市信義區忠孝東路五段XX號",
      layout_info: {
        overall_layout: "4房2廳",
        floor_info: "3樓"
      },
      rights: "可租補"
    },
    room_details: "雅房A $11,800 (含獨立衛浴)\n雅房B $12,000 (採光佳)\n雅房C $12,300 (空間較大)",
    fees: {
      electricity: "⚠️ 圖片顯示每度6元，文字說明為依台電費率",
      deposit: "2個月",
      included: "水費、網路費"
    },
    url: "https://facebook.com"
  }
];

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* 頁面表頭 */}
      <PageHeader totalListings={sampleRentals.length} />

      {/* 租屋卡片網格 */}
      <div className="max-w-6xl mx-auto px-6 py-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sampleRentals.map((rental) => (
          <RentalCard key={rental.id} rental={rental} />
        ))}
      </div>
    </main>
  );
}
