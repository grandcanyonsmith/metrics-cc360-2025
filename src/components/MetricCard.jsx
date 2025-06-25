import React from 'react';
import { cn } from '../utils/cn';
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';

const MetricCard = ({ 
  title, 
  value, 
  content,
  previousValue, 
  definition, 
  status, 
  message, 
  numerator, 
  denominator,
  onViewDetails,
  isLoading = false 
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'ok':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'missing':
        return 'text-gray-600 bg-gray-50 border-gray-200';
      case 'partial':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getTrendIcon = () => {
    if (!previousValue || value === null || previousValue === null) return <Minus className="w-4 h-4 text-gray-400" />;
    
    const change = value - previousValue;
    if (change > 0) return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (change < 0) return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const formatValue = (val) => {
    if (val === null || val === undefined) return 'N/A';
    if (typeof val === 'number') {
      if (val >= 1) return val.toLocaleString();
      if (val > 0 && val < 1) return `${(val * 100).toFixed(1)}%`;
      return val.toString();
    }
    return val;
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'ok': return 'Good';
      case 'warning': return 'Warning';
      case 'error': return 'Error';
      case 'missing': return 'Missing';
      case 'partial': return 'Partial';
      default: return 'Unknown';
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'ok':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'missing':
        return 'bg-gray-100 text-gray-800';
      case 'partial':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className={cn(
      "bg-white rounded-lg border p-6 shadow-sm hover:shadow-md transition-shadow",
      getStatusColor(status)
    )}>
      {/* Custom status message at the top */}
      {message && (status === 'warning' || status === 'error') && (
        <div className={cn(
          "mb-4 px-3 py-2 text-sm font-medium rounded-md",
          getStatusBadgeColor(status)
        )}>
          {message}
        </div>
      )}
      
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
          {definition && (
            <p className="text-sm text-gray-600 mb-2">{definition}</p>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {getTrendIcon()}
          <span className={cn(
            "px-2 py-1 text-xs font-medium rounded-full",
            getStatusBadgeColor(status)
          )}>
            {getStatusText(status)}
          </span>
        </div>
      </div>

      {isLoading ? (
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      ) : (
        <>
          {content ? (
            <div className="mb-4">
              {content}
            </div>
          ) : (
            <div className="mb-4">
              <div className="text-3xl font-bold text-gray-900 mb-1">
                {formatValue(value)}
              </div>
              {numerator !== undefined && denominator !== undefined && (
                <div className="text-sm text-gray-500">
                  {numerator.toLocaleString()} / {denominator.toLocaleString()}
                </div>
              )}
            </div>
          )}

          {message && !(status === 'warning' || status === 'error') && (
            <div className="flex items-start space-x-2 p-3 bg-blue-50 rounded-md mb-4">
              <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-blue-700">{message}</p>
            </div>
          )}

          {onViewDetails && status === 'ok' && (
            <button
              onClick={onViewDetails}
              className="w-full mt-4 px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 border border-primary-200 rounded-md hover:bg-primary-100 transition-colors"
            >
              View Details
            </button>
          )}
        </>
      )}
    </div>
  );
};

export default MetricCard; 