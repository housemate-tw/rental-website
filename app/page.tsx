"use client";

import React, { useState, useMemo, useEffect } from 'react';
import RentalCard from '@/components/RentalCard';
import PageHeader from '@/components/PageHeader';
import FilterBar from '@/components/FilterBar';

export default function Home() {
  // 租屋資料狀態
  const [rentals, setRentals] = useState([]);
  const [loading, setLoading] = useState(true);

  // 篩選狀態管理
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedHousingType, setSelectedHousingType] = useState('');

  // 載入真實資料
  useEffect(() => {
    // 使用環境變數中的 basePath，fallback 到空字串
    const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
    const dataPath = `${basePath}/data/rentals.json`;

    console.log('嘗試載入資料從:', dataPath);
    console.log('basePath:', basePath);
    console.log('當前 URL:', window.location.href);

    fetch(dataPath)
      .then(res => {
        console.log('Fetch response status:', res.status);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        console.log('資料載入成功，物件數量:', data.length);
        setRentals(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('載入資料失敗:', error);
        console.error('錯誤詳情:', error.message);
        setLoading(false);
      });
  }, []);

  // 篩選邏輯
  const filteredRentals = useMemo(() => {
    return rentals.filter((rental: any) => {
      // 區域篩選
      if (selectedDistrict && rental.district !== selectedDistrict) {
        return false;
      }

      // 房型篩選
      if (selectedHousingType && rental.housing_type !== selectedHousingType) {
        return false;
      }

      return true;
    });
  }, [rentals, selectedDistrict, selectedHousingType]);

  // 清除所有篩選
  const handleClearFilters = () => {
    setSelectedDistrict('');
    setSelectedHousingType('');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* 頁面表頭 */}
      <PageHeader totalListings={filteredRentals.length} />

      {/* 篩選列 */}
      <FilterBar
        selectedDistrict={selectedDistrict}
        selectedHousingType={selectedHousingType}
        onDistrictChange={setSelectedDistrict}
        onHousingTypeChange={setSelectedHousingType}
        onClearFilters={handleClearFilters}
      />

      {/* 租屋卡片網格 */}
      <div className="max-w-6xl mx-auto px-6 py-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-12">
            <p className="text-lg font-medium text-gray-500">載入中...</p>
          </div>
        ) : filteredRentals.length > 0 ? (
          filteredRentals.map((rental: any) => (
            <RentalCard key={rental.id} rental={rental} />
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-lg font-medium text-gray-500">
              找不到符合條件的物件
            </p>
            <button
              onClick={handleClearFilters}
              className="mt-4 text-sm font-medium underline"
              style={{ color: '#334155' }}
            >
              清除篩選條件
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
