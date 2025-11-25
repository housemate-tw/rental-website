import RentalItemCodex from '@/components/RentalItemCodex';
import { CodexRental } from '@/lib/codexRentalMapper';

export default async function CodexPage() {
  let rentals: CodexRental[] = [];
  let error: string | null = null;

  try {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const res = await fetch(`${baseUrl}/api/rentals-codex`, {
      cache: 'no-store',
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch rentals: ${res.status} ${res.statusText}`);
    }
    rentals = await res.json();
  } catch (e: any) {
    console.error('codex page fetch error:', e);
    error = e.message || 'Unknown error';
  }

  return (
    <main className="flex min-h-screen flex-col items-start p-6">
      <div className="max-w-5xl w-full py-8 text-left">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4">
          Codex 專用：結構化摘要筆記版本
        </h1>
        <p className="text-base text-gray-600 mb-6">
          來源：/rental_scraper_MAIN/data/processed/structured_*.jsonl → /api/rentals-codex
          （notes 由 summary_notes 轉換，超過 3 行可展開查看更多）
        </p>
        <hr className="border-t border-gray-200 my-6" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-5xl mx-auto">
        {error && <p className="text-red-500 text-lg col-span-full">Error: {error}</p>}
        {rentals.length === 0 && !error && (
          <p className="text-gray-500 text-lg col-span-full">沒有找到租屋資料。</p>
        )}
        {rentals.map((rental) => (
          <RentalItemCodex key={rental.id} rental={rental} />
        ))}
      </div>
    </main>
  );
}
