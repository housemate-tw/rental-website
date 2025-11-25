import { Inter } from 'next/font/google';
import RentalItem from '@/components/RentalItem';
import { Clock } from 'lucide-react';
import fs from 'fs';
import path from 'path';

const inter = Inter({ subsets: ['latin'] });

interface Rental {
  id: string;
  sequence: number;
  notes: string;
  rent: string;
  district: string;
  housing_type: string;
  raw_post: string;
  processed_date: string;
  processed_time: string;
  version: string;
  validation_issues: string[] | null;
  url?: string;
}

async function getRentals(): Promise<Rental[]> {
  const dataDir = '/Users/sabrina/Documents/data_v8';
  const allRentals: Rental[] = [];

  try {
    const filenames = fs.readdirSync(dataDir);
    const jsonlFiles = filenames.filter(file => file.endsWith('.jsonl'));

    for (const fileName of jsonlFiles) {
      const filePath = path.join(dataDir, fileName);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const lines = fileContent.split('\n');

      for (const line of lines) {
        if (line.trim() !== '') {
          try {
            allRentals.push(JSON.parse(line));
          } catch (e) {
            console.error(`Error parsing JSON from ${fileName}:`, e);
          }
        }
      }
    }

    allRentals.sort((a, b) => {
      const dateA = new Date(`${a.processed_date}T${a.processed_time}`);
      const dateB = new Date(`${b.processed_date}T${b.processed_time}`);
      return dateB.getTime() - dateA.getTime();
    });

    return allRentals;
  } catch (error) {
    console.error('Error reading rental data:', error);
    return [];
  }
}

export default async function Home() {
  const rentals = await getRentals();
  const error = rentals.length === 0 ? '無法載入租屋資料' : null;

  return (
    <main className={`flex min-h-screen flex-col items-start p-6 ${inter.className}`}>
      <div className="max-w-5xl w-full py-8 text-right ml-auto">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4">大台北租屋社團最新物件彙整</h1>
        <div className="flex items-center justify-end text-base text-gray-600 mb-2">
          <Clock size={18} className="mr-2 text-blue-500" />
          <span>每日更新 24 小時內最新物件</span>
        </div>
        <p className="text-base text-gray-600 mb-6">一次看完 FB 各大熱門租屋社團最新物件</p>
        <div className="flex flex-wrap justify-end gap-x-4 gap-y-2 text-sm font-medium text-purple-700 mb-8">
          <span>雅房｜分租套房｜ 獨立套房</span>
          <span>租金 $5,000～$20,000｜大台北地區</span>
        </div>
        <hr className="border-t border-gray-200 my-6" /> {/* Separator */}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-5xl mx-auto">
        {error && <p className="text-red-500 text-lg col-span-full">Error: {error}</p>}
        {rentals.length === 0 && !error && <p className="text-gray-500 text-lg col-span-full">沒有找到租屋資料。</p>}
        {rentals.map((rental) => (
          <RentalItem key={rental.id} rental={rental} />
        ))}
      </div>
    </main>
  );
}