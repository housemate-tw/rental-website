import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { mapCodexRental, sortCodexRentals } from '@/lib/codexRentalMapper';

export const dynamic = 'force-static';

// Codex: 讀取結構化結果,轉為前端友善的 notes/highlights 欄位
export async function GET() {
  const dataDir = path.resolve('/Users/sabrina/Documents/rental_scraper_MAIN/data/processed');
  let rentals: any[] = [];

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
          console.error(`codex route parse error in ${fileName}:`, line, e);
        }
      }
    }

    rentals.sort(sortCodexRentals);
    return NextResponse.json(rentals);
  } catch (error) {
    console.error('codex route error reading rentals:', error);
    return NextResponse.json({ error: 'Failed to load codex rentals' }, { status: 500 });
  }
}
