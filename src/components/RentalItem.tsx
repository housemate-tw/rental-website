import { MapPin, DollarSign, Building, Link, Calendar } from 'lucide-react';

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

interface RentalItemProps {
  rental: Rental;
}

const RentalItem: React.FC<RentalItemProps> = ({ rental }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 ease-in-out flex flex-col mb-6">
      {/* Notes - Most prominent */}
      <p className="text-gray-900 text-xl font-extrabold mb-4 leading-snug">
        {rental.notes}
      </p>

      {/* District, Housing Type, Rent, Processed Date - Balanced and with Icons */}
      <div className="space-y-2 text-sm text-gray-700">
        <div className="flex items-center">
          <MapPin size={18} className="mr-2 text-blue-600" />
          <span className="font-semibold">{rental.district}</span>
          <span className="mx-2 text-gray-400">|</span>
          <Building size={18} className="mr-2 text-blue-600" />
          <span>{rental.housing_type}</span>
        </div>
        <div className="flex items-center">
          <DollarSign size={18} className="mr-2 text-purple-600" />
          <span>租金: <span className="font-bold text-lg">${rental.rent}</span></span>
        </div>
        <div className="flex items-center">
          <Calendar size={16} className="mr-2 text-gray-400" />
          <span>刊登時間: {rental.processed_date}</span>
        </div>
      </div>

      {/* CTA Button - Gogoro inspired rounded button */}
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

export default RentalItem;
