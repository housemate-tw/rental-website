import RentalItemCodex from '@/components/RentalItemCodex';
import { CodexRental, mapCodexRental, sortCodexRentals } from '@/lib/codexRentalMapper';
import fs from 'fs';
import path from 'path';

async function getCodexRentals(): Promise<CodexRental[]> {
  const dataDir = '/Users/sabrina/Documents/rental_scraper_MAIN/data/processed';
  const rentals: CodexRental[] = [];

  try {
    const filenames = fs.readdirSync(dataDir);
    const jsonlFiles = filenames.filter(
      (file) => file.startsWith('structured_') && file.endsWith('.jsonl'),
    );

    for (const fileName of jsonlFiles) {
      const filePath = path.join(dataDir, fileName);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const lines = fileContent.split('\n');

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          rentals.push(mapCodexRental(parsed));
        } catch (e) {
          console.error(`Error parsing ${fileName}:`, e);
        }
      }
    }

    rentals.sort(sortCodexRentals);
    return rentals;
  } catch (error) {
    console.error('Error reading codex rentals:', error);
    return [];
  }
}

export default async function CodexPage() {
  const rentals = await getCodexRentals();
  const error = rentals.length === 0 ? '無法載入租屋資料' : null;

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
