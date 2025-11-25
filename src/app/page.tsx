import { Inter } from 'next/font/google';
import RentalItem from '@/components/RentalItem';
import { Clock } from 'lucide-react'; // Import Clock icon

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
  url?: string; // Optional URL field
}

export default async function Home() {
  let rentals: Rental[] = [];
  let error: string | null = null;

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/api/rentals`, {
      cache: 'no-store',
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch rentals: ${res.status} ${res.statusText}`);
    }
    rentals = await res.json();
  } catch (e: any) {
    console.error('Error fetching rentals:', e);
    error = e.message || 'An unknown error occurred';
  }

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