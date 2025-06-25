import React from 'react';
import { X } from 'lucide-react';
import { cn } from '../utils/cn';

const MetricDetailsModal = ({ isOpen, onClose, metric, data, isLoading, showOnlyNonActivated, setShowOnlyNonActivated, showOnlyDormant, setShowOnlyDormant, metrics, onViewDetails }) => {
  if (!isOpen) return null;

  const getMetricTitle = (metric) => {
    const titles = {
      'dormant_account_rate': 'Dormant Account Rate',
      'involuntary_churn_rate': 'Involuntary Churn Rate',
      'dunning_recovery_rate': 'Dunning Recovery Rate',
      't24h_activation_rate': '24h Activation Rate',
      'source_attribution_coverage': 'Source Attribution Coverage',
      'cac_to_ltv': 'CAC to LTV Ratio Breakdown',
    };
    return titles[metric] || metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getColumnHeaders = (metric) => {
    const headers = {
      'dormant_account_rate': ['Customer ID', 'First Purchase', 'Email', 'Customer Name', 'Subscription ID'],
      'involuntary_churn_rate': ['Customer ID', 'Canceled At', 'Email'],
      'dunning_recovery_rate': ['Invoice ID', 'Customer ID', 'Paid At', 'Email'],
      't24h_activation_rate': ['Customer ID', 'First Purchase', 'Activation Time', 'Email', 'Customer Name'],
      'source_attribution_coverage': ['ID', 'Campaign Source', 'Campaign Medium', 'Campaign Name', 'Timestamp'],
    };
    return headers[metric] || Object.keys(data[0] || {}).map(key => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {getMetricTitle(metric)} Details
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          {/* Special case for CAC to LTV Ratio - show nested cards */}
          {metric === 'cac_to_ltv' ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* CAC Card */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Customer Acquisition Cost</h3>
                    <span className="text-2xl font-bold text-blue-600">
                      {metrics?.cac?.value ? `$${metrics.cac.value.toFixed(2)}` : 'N/A'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    Total ad spend divided by total new trials
                  </p>
                  <div className="text-xs text-gray-500 mb-4">
                    {metrics?.cac?.message || 'No data available'}
                  </div>
                  <button
                    onClick={() => onViewDetails('cac')}
                    className="w-full bg-blue-50 text-blue-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-100 transition-colors"
                  >
                    View Details
                  </button>
                </div>

                {/* LTV Card */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Gross Profit LTV</h3>
                    <span className="text-2xl font-bold text-green-600">
                      {metrics?.ltv?.value ? `$${metrics.ltv.value.toFixed(2)}` : 'N/A'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    Average gross profit per customer over their lifetime (revenue - $229 cost)
                  </p>
                  <div className="text-xs text-gray-500 mb-4">
                    {metrics?.ltv?.message || 'No data available'}
                  </div>
                  <button
                    onClick={() => onViewDetails('ltv')}
                    className="w-full bg-green-50 text-green-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-green-100 transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>

              {/* Ratio Summary */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Ratio Summary</h3>
                <div className="text-sm text-gray-600">
                  {metrics?.cac_to_ltv?.message || 'No ratio data available'}
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Toggle for 24h Activation Rate */}
              {metric === 't24h_activation_rate' && setShowOnlyNonActivated && (
                <div className="mb-4 flex items-center">
                  <input
                    id="show-non-activated"
                    type="checkbox"
                    checked={showOnlyNonActivated}
                    onChange={e => setShowOnlyNonActivated(e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="show-non-activated" className="text-sm text-gray-700">
                    Show only non-activated users
                  </label>
                </div>
              )}
              {/* Toggle for Dormant Account Rate */}
              {metric === 'dormant_account_rate' && setShowOnlyDormant && (
                <div className="mb-4 flex items-center">
                  <input
                    id="show-only-dormant"
                    type="checkbox"
                    checked={showOnlyDormant}
                    onChange={e => setShowOnlyDormant(e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="show-only-dormant" className="text-sm text-gray-700">
                    Show only dormant users
                  </label>
                </div>
              )}
              {isLoading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  ))}
                </div>
              ) : data && data.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        {getColumnHeaders(metric).map((header, index) => (
                          <th
                            key={index}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {data.map((row, rowIndex) => (
                        <tr key={rowIndex} className="hover:bg-gray-50">
                          {metric === 'involuntary_churn_rate' ? (
                            <>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {row.customer_id || 'N/A'}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {row.canceled_at && 
                                 typeof row.canceled_at === 'string' && 
                                 row.canceled_at.includes('T') 
                                  ? formatDate(row.canceled_at) 
                                  : row.canceled_at || 'N/A'}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {row.email || 'N/A'}
                              </td>
                            </>
                          ) : (
                            Object.values(row).map((value, colIndex) => (
                              <td
                                key={colIndex}
                                className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                              >
                                {typeof value === 'string' && value.includes('T') 
                                  ? formatDate(value) 
                                  : value || 'N/A'}
                              </td>
                            ))
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">No data available for this metric in the selected date range.</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricDetailsModal; 