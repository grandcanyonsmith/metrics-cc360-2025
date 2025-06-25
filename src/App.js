import React, { useState, useEffect } from 'react';
import { subDays } from 'date-fns';
import { fetchDashboardMetrics, fetchMetricDetails } from './services/api';
import MetricCard from './components/MetricCard';
import DateRangePicker from './components/DateRangePicker';
import MetricDetailsModal from './components/MetricDetailsModal';
import { BarChart3, TrendingUp, Users, CreditCard, Activity, Target, Monitor, Calendar, AlertTriangle, DollarSign } from 'lucide-react';

function App() {
  const [startDate, setStartDate] = useState(subDays(new Date(), 30));
  const [endDate, setEndDate] = useState(new Date());
  const [metrics, setMetrics] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [metricDetails, setMetricDetails] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showOnlyNonActivated, setShowOnlyNonActivated] = useState(false);
  const [showOnlyDormant, setShowOnlyDormant] = useState(false);

  const metricConfigs = {
    'dormant_account_rate': {
      title: 'Dormant Account Rate',
      icon: Users,
      description: 'Percentage of new purchasers with zero sessions after first purchase',
      format: 'percentage',
      category: 'Customer Success'
    },
    'involuntary_churn_rate': {
      title: 'Involuntary Churn Rate',
      icon: CreditCard,
      description: 'Percentage of subscriptions canceled due to failed payments',
      format: 'percentage',
      category: 'Finance'
    },
    'dunning_recovery_rate': {
      title: 'Dunning Recovery Rate',
      icon: AlertTriangle,
      description: 'Percentage of failed payments that were successfully recovered',
      format: 'percentage',
      category: 'Finance'
    },
    't24h_activation_rate': {
      title: '24h Activation Rate',
      icon: Target,
      description: 'Percentage of new users who performed a key action within 24 hours',
      format: 'percentage',
      category: 'Customer Success'
    },
    // 'cac': {
    //   title: 'Customer Acquisition Cost',
    //   icon: DollarSign,
    //   description: 'Total ad spend divided by total new trials',
    //   format: 'currency',
    //   category: 'Marketing'
    // },
    // 'ltv': {
    //   title: 'Gross Profit LTV',
    //   icon: DollarSign,
    //   description: 'Average gross profit per customer over their lifetime (revenue - $229 cost)',
    //   format: 'currency',
    //   category: 'Marketing'
    // },
    'cac_to_ltv_ratio': {
      title: 'CAC to LTV Ratio',
      icon: TrendingUp,
      description: 'LTV divided by CAC - shows return on customer acquisition investment',
      format: 'ratio',
      category: 'Marketing'
    },
    'facebook_cac_to_ltv_ratio': {
      title: 'Facebook CAC to LTV Ratio',
      icon: TrendingUp,
      description: 'Facebook-specific CAC to LTV ratio for sales from Facebook ads',
      format: 'ratio',
      category: 'Marketing'
    },
    'facebook_lead_cac_to_ltv_ratio': {
      title: 'Facebook Lead CAC to LTV',
      icon: TrendingUp,
      description: 'CAC to LTV ratio specifically for Facebook Lead Ads',
      format: 'ratio',
      category: 'Marketing'
    },
    'mrr_to_ad_spend': {
      title: 'MRR to Ad Spend %',
      icon: DollarSign,
      description: 'Percentage of Monthly Recurring Revenue spent on advertising',
      format: 'percentage',
      category: 'Financial'
    },
    'platform_breakdown': {
      title: 'Platform Breakdown',
      icon: Monitor,
      description: 'Top platforms by event count',
      format: 'list',
      category: 'Product & IT'
    },
    'root_cause_pareto': {
      title: 'Root Cause Pareto',
      icon: Activity,
      description: 'Top payment failure reasons',
      format: 'pareto',
      category: 'Finance'
    },
    'facebook_lead_ads_total': {
      title: 'Facebook Lead Ads Total',
      icon: DollarSign,
      description: 'Total count of Facebook lead ads in the selected date range',
      format: 'number',
      category: 'Marketing'
    },
    // 'daily_trends': {
    //   title: 'Daily Event Trends',
    //   icon: Calendar,
    //   description: 'Daily event counts and user activity',
    //   format: 'trends',
    //   category: 'Product & IT'
    // }
  };

  useEffect(() => {
    fetchMetrics();
  }, [startDate, endDate]);

  const fetchMetrics = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await fetchDashboardMetrics(
        
        startDate.toISOString(),
        endDate.toISOString()
      );
      setMetrics(data);
      console.log('data', data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setError('Failed to load metrics. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewDetails = async (metric) => {
    setSelectedMetric(metric);
    setIsModalOpen(true);
    setIsDetailsLoading(true);
    let extraParams = {};
    if (metric === 't24h_activation_rate' && showOnlyNonActivated) {
      extraParams.activated = 'false';
    }
    if (metric === 'dormant_account_rate' && showOnlyDormant) {
      extraParams.dormant = 'true';
    }
    // Log for debugging
    console.log('Fetching details for', metric, 'from', startDate.toISOString(), 'to', endDate.toISOString(), 'params:', extraParams);
    try {
      const details = await fetchMetricDetails(
        metric,
        startDate.toISOString(),
        endDate.toISOString(),
        extraParams
      );
      setMetricDetails(details);
    } catch (error) {
      console.error('Failed to fetch metric details:', error);
      setMetricDetails([]);
    } finally {
      setIsDetailsLoading(false);
    }
  };

  useEffect(() => {
    if (isModalOpen && selectedMetric === 't24h_activation_rate') {
      handleViewDetails('t24h_activation_rate');
    }
    // eslint-disable-next-line
  }, [showOnlyNonActivated]);

  useEffect(() => {
    if (isModalOpen && selectedMetric === 'dormant_account_rate') {
      handleViewDetails('dormant_account_rate');
    }
    // eslint-disable-next-line
  }, [showOnlyDormant]);

  const handleDateChange = (newStartDate, newEndDate) => {
    setStartDate(newStartDate);
    setEndDate(newEndDate);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedMetric(null);
    setMetricDetails([]);
  };

  const formatValue = (value, format) => {
    if (value === null || value === undefined) return 'N/A';
    
    switch (format) {
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'currency':
        return `$${value.toFixed(2)}`;
      case 'ratio':
        return `${value.toFixed(1)}x`;
      case 'number':
        return value.toLocaleString();
      default:
        return value.toString();
    }
  };

  const renderPlatformBreakdown = (data) => {
    
    if (!data || !Array.isArray(data)) return null;
    
    return (
      <div className="space-y-2">
        {data.slice(0, 3).map((platform, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span className="text-gray-600">{platform.platform}</span>
            <span className="font-medium">{platform.event_count.toLocaleString()}</span>
          </div>
        ))}
        {data.length > 3 && (
          <div className="text-xs text-gray-500 text-center">
            +{data.length - 3} more platforms
          </div>
        )}
      </div>
    );
  };

  const renderParetoBreakdown = (data) => {
    if (!data || !Array.isArray(data)) return null;
    return (
      <div className="space-y-2">
        {data.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between">
            <span className="bg-purple-700/80 text-white px-2 py-1 rounded font-mono text-xs">
              {item.reason}
            </span>
            <span className="bg-gray-900/80 text-white px-2 py-1 rounded font-mono text-base font-bold">
              {item.count.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-primary-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">SaaS Metrics Dashboard</h1>
            </div>
            <div className="text-sm text-gray-500">
              {startDate.toLocaleDateString()} - {endDate.toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Date Range Picker always visible */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <DateRangePicker
          startDate={startDate}
          endDate={endDate}
          onDateChange={handleDateChange}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading metrics</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Group metrics by category */}
        {['Marketing', 'Customer Success', 'Finance', 'Sales', 'Product & IT'].map(category => {
          const categoryMetrics = Object.entries(metricConfigs).filter(([, config]) => config.category === category);
          if (categoryMetrics.length === 0) return null;
          return (
            <div key={category} className="mb-10">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">{category}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {categoryMetrics.map(([key, config]) => {
                  const metric = metrics[key];
                  const Icon = config.icon;
                  if (!metric) {
                    return (
                      <MetricCard
                        key={key}
                        title={config.title}
                        value={null}
                        definition={config.description}
                        status="missing"
                        message="No data available"
                        isLoading={isLoading}
                      />
                    );
                  }
                  let displayValue = null;
                  let displayContent = null;
                  let customStatus = metric.status || 'ok';
                  let customStatusMessage = null;
                  
                  if (config.format === 'list' && metric.data) {
                    displayContent = renderPlatformBreakdown(metric.data);
                  } else if (config.format === 'pareto' && metric.data) {
                    displayContent = renderParetoBreakdown(metric.data);
                  } else if (metric.value !== null && metric.value !== undefined) {
                    displayValue = formatValue(metric.value, config.format);
                  }
                  
                  // Custom status logic for specific metrics
                  if (key === 'cac_to_ltv_ratio' && metric.value !== null) {
                    if (metric.value < 2) {
                      customStatus = 'error';
                      customStatusMessage = 'Overspending';
                    } else if (metric.value < 3) {
                      customStatus = 'warning';
                      customStatusMessage = 'Slightly Overspending';
                    } else if (metric.value > 5) {
                      customStatus = 'error';
                      customStatusMessage = 'Underspending';
                    } else if (metric.value > 4) {
                      customStatus = 'warning';
                      customStatusMessage = 'Slightly Underspending';
                    }
                  } else if (key === 'mrr_to_ad_spend' && metric.value !== null) {
                    if (metric.value > 0.20) { // 20%
                      customStatus = 'error';
                      customStatusMessage = 'Overspending';
                    } else if (metric.value > 0.175) { // 17.5%
                      customStatus = 'warning';
                      customStatusMessage = 'Slightly Overspending';
                    } else if (metric.value < 0.10) { // 10%
                      customStatus = 'error';
                      customStatusMessage = 'Underspending';
                    } else if (metric.value < 0.125) { // 12.5%
                      customStatus = 'warning';
                      customStatusMessage = 'Slightly Underspending';
                    }
                  }
                  
                  return (
                    <MetricCard
                      key={key}
                      title={config.title}
                      value={displayValue}
                      content={displayContent}
                      definition={config.description}
                      status={customStatus}
                      message={customStatusMessage || metric.message}
                      numerator={metric.numerator}
                      denominator={metric.denominator}
                      onViewDetails={() => handleViewDetails(key)}
                      isLoading={isLoading}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Additional sections for detailed data */}
        {/* Daily Event Trends section removed */}
      </div>

      <MetricDetailsModal
        isOpen={isModalOpen}
        onClose={closeModal}
        metric={selectedMetric}
        data={metricDetails}
        isLoading={isDetailsLoading}
        showOnlyNonActivated={showOnlyNonActivated}
        setShowOnlyNonActivated={setShowOnlyNonActivated}
        showOnlyDormant={showOnlyDormant}
        setShowOnlyDormant={setShowOnlyDormant}
        metrics={metrics}
        onViewDetails={handleViewDetails}
      />
    </div>
  );
}

export default App; 