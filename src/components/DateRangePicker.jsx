import React from 'react';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { format, subDays, addDays } from 'date-fns';

const DateRangePicker = ({ startDate, endDate, onDateChange }) => {
  const quickRanges = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 90 days', days: 90 },
    { label: 'Last 6 months', days: 180 },
  ];

  const handleQuickRange = (days) => {
    const newEndDate = new Date();
    const newStartDate = subDays(newEndDate, days);
    onDateChange(newStartDate, newEndDate);
  };

  const handleDateInput = (type, value) => {
    const date = new Date(value);
    if (type === 'start') {
      onDateChange(date, endDate);
    } else {
      onDateChange(startDate, date);
    }
  };

  const navigateDays = (direction) => {
    const days = direction === 'forward' ? 1 : -1;
    const newStartDate = addDays(startDate, days);
    const newEndDate = addDays(endDate, days);
    onDateChange(newStartDate, newEndDate);
  };

  return (
    <div className="bg-white rounded-lg border p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Date Range</h2>
        <Calendar className="w-5 h-5 text-gray-400" />
      </div>

      <div className="flex items-center space-x-4 mb-4">
        <button
          onClick={() => navigateDays('back')}
          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center space-x-2">
          <input
            type="date"
            value={format(startDate, 'yyyy-MM-dd')}
            onChange={(e) => handleDateInput('start', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <span className="text-gray-500">to</span>
          <input
            type="date"
            value={format(endDate, 'yyyy-MM-dd')}
            onChange={(e) => handleDateInput('end', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <button
          onClick={() => navigateDays('forward')}
          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {quickRanges.map((range) => (
          <button
            key={range.days}
            onClick={() => handleQuickRange(range.days)}
            className="px-3 py-1 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default DateRangePicker; 