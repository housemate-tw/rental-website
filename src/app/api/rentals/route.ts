import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-static';

export async function GET() {
  const dataDir = path.resolve('/Users/sabrina/Documents/data_v8');
  let allRentals: any[] = [];

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
            console.error(`Error parsing JSON from line in ${fileName}:`, line, e);
          }
        }
      }
    }

    // Sort by date and sequence, most recent first
    allRentals.sort((a, b) => {
      const dateA = new Date(`${a.processed_date}T${a.processed_time}`);
      const dateB = new Date(`${b.processed_date}T${b.processed_time}`);
      return dateB.getTime() - dateA.getTime();
    });

    return NextResponse.json(allRentals);
  } catch (error) {
    console.error('Error reading rental data:', error);
    return NextResponse.json({ error: 'Failed to load rental data' }, { status: 500 });
  }
}
