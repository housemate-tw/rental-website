"use client";

import { useState } from 'react';
import { MapPin, DollarSign, Building, Link, Calendar, ChevronDown, ChevronUp } from 'lucide-react';
import { CodexRental } from '@/lib/codexRentalMapper';

interface Props {
  rental: CodexRental;
}

const RentalItemCodex: React.FC<Props> = ({ rental }) => {
  const [expanded, setExpanded] = useState(false);
  const visibleHighlights = expanded ? rental.summary_notes ?? rental.highlights : rental.highlights;
  const shouldShowToggle = (rental.summary_notes?.length || 0) > 3;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 ease-in-out flex flex-col mb-6">
      {visibleHighlights && visibleHighlights.length > 0 ? (
        <ul className="text-gray-900 text-base font-semibold mb-4 leading-relaxed list-disc list-inside space-y-1">
          {visibleHighlights.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-900 text-lg font-semibold mb-4 leading-snug">{rental.notes}</p>
      )}

      {shouldShowToggle && (
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors mb-4"
        >
          {expanded ? (
            <>
              <ChevronUp size={16} className="mr-1" />
              收起
            </>
          ) : (
            <>
              <ChevronDown size={16} className="mr-1" />
              查看更多
            </>
          )}
        </button>
      )}

      <div className="space-y-2 text-sm text-gray-700">
        <div className="flex items-center">
          <MapPin size={18} className="mr-2 text-blue-600" />
          <span className="font-semibold">{rental.district || '未提供區域'}</span>
          <span className="mx-2 text-gray-400">|</span>
          <Building size={18} className="mr-2 text-blue-600" />
          <span>{rental.housing_type || '未提供房型'}</span>
        </div>
        {rental.rent && (
          <div className="flex items-center">
            <DollarSign size={18} className="mr-2 text-purple-600" />
            <span>
              租金: <span className="font-bold text-lg">${rental.rent}</span>
            </span>
          </div>
        )}
        {(rental.processed_date || rental.processed_time) && (
          <div className="flex items-center">
            <Calendar size={16} className="mr-2 text-gray-400" />
            <span>
              刊登時間: {rental.processed_date}
              {rental.processed_time ? ` ${rental.processed_time}` : ''}
            </span>
          </div>
        )}
      </div>

      {rental.url && (
        <div className="mt-auto pt-5">
          <a
            href={rental.url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full inline-flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-full hover:bg-purple-700 text-base font-semibold transition-colors duration-200"
          >
            <Link size={20} className="mr-2" />
            點擊查看詳情
          </a>
        </div>
      )}
    </div>
  );
};

export default RentalItemCodex;
