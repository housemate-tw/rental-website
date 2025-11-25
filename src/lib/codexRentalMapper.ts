export interface CodexRental {
  id: string;
  district?: string;
  housing_type?: string;
  rent?: string;
  url?: string;
  notes: string;
  highlights: string[];
  hasMoreHighlights: boolean;
  summary_notes?: string[];
  processed_date?: string;
  processed_time?: string;
  [key: string]: any;
}

const toArray = (maybeArr: unknown): string[] => {
  if (Array.isArray(maybeArr)) {
    return maybeArr.filter((item): item is string => Boolean(item));
  }
  if (typeof maybeArr === 'string' && maybeArr.trim().length > 0) {
    return [maybeArr.trim()];
  }
  return [];
};

const deriveTimestamp = (raw: any): number => {
  if (raw?.processed_date && raw?.processed_time) {
    const date = new Date(`${raw.processed_date}T${raw.processed_time}`);
    const time = date.getTime();
    if (!Number.isNaN(time)) return time;
  }

  if (typeof raw?.id === 'string') {
    const datePart = raw.id.split('_')[0];
    const date = new Date(datePart);
    const time = date.getTime();
    if (!Number.isNaN(time)) return time;
  }

  return 0;
};

export const mapCodexRental = (raw: any): CodexRental => {
  const summaryList = toArray(raw?.summary_notes);
  const highlights = summaryList.slice(0, 3);
  const hasMoreHighlights = summaryList.length > 3;
  const notesFromSummary = summaryList.join(' · ');
  const notes = notesFromSummary || raw?.notes || raw?.raw_post || '';

  return {
    ...raw,
    notes,
    highlights,
    hasMoreHighlights,
    summary_notes: summaryList,
    _codex_ts: deriveTimestamp(raw),
  };
};

export const sortCodexRentals = (a: CodexRental, b: CodexRental) =>
  (b as any)._codex_ts - (a as any)._codex_ts;
