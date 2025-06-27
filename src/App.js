import React, { useState, useEffect, useCallback } from 'react';
import { subDays, format } from 'date-fns';
import { fetchDashboardMetrics, fetchMetricDetails } from './services/api';
import MetricCard from './components/MetricCard';
import DateRangePicker from './components/DateRangePicker';
import MetricDetailsModal from './components/MetricDetailsModal';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  CreditCard, 
  Activity, 
  Target, 
  Monitor, 
  Calendar, 
  AlertTriangle, 
  DollarSign,
  RefreshCw,
  AlertCircle,
  Zap,
  Filter,
  Search,
  LucideLayoutGrid,
  List
} from 'lucide-react';
import { cn } from './utils/cn';

// Metric configuration object
const METRIC_CONFIGS = {
  'dormant_account_rate': {
    title: 'Dormant Account Rate',
    icon: Users,
    description: 'Percentage of new purchasers with zero sessions after first purchase',
    format: 'percentage',
    category: 'Customer Success',
    color: 'bg-red-50 border-red-200 text-red-700',
    trend: 'down',
    trendValue: '-2.3%'
  },
  'involuntary_churn_rate': {
    title: 'Involuntary Churn Rate',
    icon: CreditCard,
    description: 'Percentage of subscriptions canceled due to failed payments',
    format: 'percentage',
    category: 'Finance',
    color: 'bg-orange-50 border-orange-200 text-orange-700',
    trend: 'up',
    trendValue: '+1.1%'
  },
  'dunning_recovery_rate': {
    title: 'Dunning Recovery Rate',
    icon: AlertTriangle,
    description: 'Percentage of failed payments that were successfully recovered',
    format: 'percentage',
    category: 'Finance',
    color: 'bg-green-50 border-green-200 text-green-700',
    trend: 'up',
    trendValue: '+5.2%'
  },
  't24h_activation_rate': {
    title: '24h Activation Rate',
    icon: Target,
    description: 'Percentage of new users who performed a key action within 24 hours',
    format: 'percentage',
    category: 'Customer Success',
    color: 'bg-blue-50 border-blue-200 text-blue-700',
    trend: 'up',
    trendValue: '+3.8%'
  },
  'cac_to_ltv_ratio': {
    title: 'CAC to LTV Ratio',
    icon: TrendingUp,
    description: 'LTV divided by CAC - shows return on customer acquisition investment',
    format: 'ratio',
    category: 'Marketing',
    color: 'bg-purple-50 border-purple-200 text-purple-700',
    trend: 'up',
    trendValue: '+0.2'
  },
  'facebook_lead_cac_to_ltv_ratio': {
    title: 'Facebook Lead CAC to LTV',
    icon: TrendingUp,
    description: 'CAC to LTV ratio specifically for Facebook Lead Ads',
    format: 'ratio',
    category: 'Marketing',
    color: 'bg-cyan-50 border-cyan-200 text-cyan-700',
    trend: 'up',
    trendValue: '+0.3'
  },
  'mrr_to_ad_spend': {
    title: 'MRR to Ad Spend %',
    icon: DollarSign,
    description: 'Percentage of Monthly Recurring Revenue spent on advertising',
    format: 'percentage',
    category: 'Financial',
    color: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    trend: 'down',
    trendValue: '-1.5%'
  },
  'platform_breakdown': {
    title: 'Platform Breakdown',
    icon: Monitor,
    description: 'Top platforms by event count',
    format: 'list',
    category: 'Product & IT',
    color: 'bg-gray-50 border-gray-200 text-gray-700'
  },
  'root_cause_pareto': {
    title: 'Root Cause Pareto',
    icon: Activity,
    description: 'Top payment failure reasons',
    format: 'pareto',
    category: 'Finance',
    color: 'bg-rose-50 border-rose-200 text-rose-700'
  },
  'facebook_lead_ads_total': {
    title: 'Facebook Lead Ads Total',
    icon: DollarSign,
    description: 'Total count of Facebook lead ads in the selected date range',
    format: 'number',
    category: 'Marketing',
    color: 'bg-pink-50 border-pink-200 text-pink-700',
    trend: 'up',
    trendValue: '+12%'
  }
};

// Category colors for grouping
const CATEGORY_COLORS = {
  'Customer Success': 'bg-blue-50 border-blue-200',
  'Finance': 'bg-green-50 border-green-200',
  'Marketing': 'bg-purple-50 border-purple-200',
  'Financial': 'bg-emerald-50 border-emerald-200',
  'Product & IT': 'bg-gray-50 border-gray-200'
};

function App() {
  // State management
  const [startDate, setStartDate] = useState(subDays(new Date(), 30));
  const [endDate, setEndDate] = useState(new Date());
  const [metrics, setMetrics] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [metricDetails, setMetricDetails] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showOnlyNonActivated, setShowOnlyNonActivated] = useState(false);
  const [showOnlyDormant, setShowOnlyDormant] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [searchTerm, setSearchTerm] = useState('');

  // Get unique categories
  const categories = ['All', ...new Set(Object.values(METRIC_CONFIGS).map(config => config.category))];

  // Filter metrics by category and search
  const filteredMetrics = Object.entries(metrics).filter(([key, metric]) => {
    const config = METRIC_CONFIGS[key];
    if (!config) return false;
    
    // Category filter
    if (selectedCategory !== 'All' && config.category !== selectedCategory) {
      return false;
    }
    
    // Search filter
    if (searchTerm && !config.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !config.description.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    return true;
  });

  // Fetch metrics data
  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await fetchDashboardMetrics(
        startDate.toISOString(),
        endDate.toISOString()
      );
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setError('Failed to load metrics. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate]);

  // Refresh metrics
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchMetrics();
    setIsRefreshing(false);
  };

  // Handle view details
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

  // Handle date change
  const handleDateChange = (newStartDate, newEndDate) => {
    setStartDate(newStartDate);
    setEndDate(newEndDate);
  };

  // Close modal
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedMetric(null);
    setMetricDetails([]);
  };

  // Format metric value
  const formatMetricValue = (metric, config) => {
    if (metric.status === 'error') {
      return 'Error';
    }

    const value = metric.value;
    if (value === null || value === undefined) {
      return 'N/A';
    }

    switch (config.format) {
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'ratio':
        return value.toFixed(2);
      case 'number':
        return value.toLocaleString();
      default:
        return value.toString();
    }
  };

  // Render platform breakdown
  const renderPlatformBreakdown = (data) => {
    if (!data || data.length === 0) return <p className="text-gray-500">No data available</p>;
    
    return (
      <div className="space-y-2">
        {data.slice(0, 5).map((item, index) => (
          <div key={index} className="flex justify-between items-center">
            <span className="font-medium">{item.platform}</span>
            <span className="text-sm text-gray-600">
              {item.event_count.toLocaleString()} events ({item.unique_users} users)
            </span>
          </div>
        ))}
      </div>
    );
  };

  // Render Pareto breakdown
  const renderParetoBreakdown = (data) => {
    if (!data || data.length === 0) return <p className="text-gray-500">No data available</p>;
    
    const total = data.reduce((sum, item) => sum + item.count, 0);
    
    return (
      <div className="space-y-2">
        {data.slice(0, 5).map((item, index) => {
          const percentage = ((item.count / total) * 100).toFixed(1);
          return (
            <div key={index} className="space-y-1">
              <div className="flex justify-between items-center">
                <span className="font-medium">{item.reason}</span>
                <span className="text-sm text-gray-600">
                  {item.count.toLocaleString()} ({percentage}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-red-500 h-2 rounded-full transition-all duration-500" 
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Effect to fetch metrics when dates change
  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  // Effect to refresh details when filters change
  useEffect(() => {
    if (isModalOpen && selectedMetric === 't24h_activation_rate') {
      handleViewDetails('t24h_activation_rate');
    }
  }, [showOnlyNonActivated, isModalOpen, selectedMetric]);

  useEffect(() => {
    if (isModalOpen && selectedMetric === 'dormant_account_rate') {
      handleViewDetails('dormant_account_rate');
    }
  }, [showOnlyDormant, isModalOpen, selectedMetric]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="glass-effect border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0 p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold gradient-text">SaaS Metrics Dashboard</h1>
                <p className="text-gray-600 mt-1">Real-time insights into your business performance</p>
              </div>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Date Range Picker */}
        <div className="mb-8 fade-in">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onDateChange={handleDateChange}
          />
        </div>

        {/* Controls Section */}
        <div className="mb-8 space-y-4 slide-up">
          {/* Search and View Controls */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search metrics..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              />
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-200 p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-all duration-200 ${
                  viewMode === 'grid' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <LucideLayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-all duration-200 ${
                  viewMode === 'list' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-3">
            <Filter className="w-4 h-4 text-gray-500" />
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    selectedCategory === category
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300 hover:border-gray-400'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 bounce-in">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error loading metrics</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading metrics...</p>
            </div>
          </div>
        ) : (
          /* Metrics Grid/List */
          <div className={cn(
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
              : 'space-y-4'
          )}>
            {filteredMetrics.map(([key, metric], index) => {
              const config = METRIC_CONFIGS[key];
              if (!config) return null;

              return (
                <div
                  key={key}
                  className="fade-in"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <MetricCard
                    title={config.title}
                    value={formatMetricValue(metric, config)}
                    description={config.description}
                    icon={config.icon}
                    status={metric.status}
                    message={metric.message}
                    category={config.category}
                    color={config.color}
                    onClick={() => handleViewDetails(key)}
                    data={metric.data}
                    format={config.format}
                    renderPlatformBreakdown={renderPlatformBreakdown}
                    renderParetoBreakdown={renderParetoBreakdown}
                    trend={config.trend}
                    trendValue={config.trendValue}
                  />
                </div>
              );
            })}
          </div>
        )}

        {/* No Metrics Found */}
        {!isLoading && filteredMetrics.length === 0 && !error && (
          <div className="text-center py-12">
            <Monitor className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No metrics found</h3>
            <p className="text-gray-500">
              Try adjusting your search terms, date range, or category filter.
            </p>
          </div>
        )}
      </div>

      {/* Metric Details Modal */}
      <MetricDetailsModal
        isOpen={isModalOpen}
        onClose={closeModal}
        metric={selectedMetric ? METRIC_CONFIGS[selectedMetric] : null}
        data={metricDetails}
        isLoading={isDetailsLoading}
        startDate={startDate}
        endDate={endDate}
        showOnlyNonActivated={showOnlyNonActivated}
        showOnlyDormant={showOnlyDormant}
        onShowOnlyNonActivatedChange={setShowOnlyNonActivated}
        onShowOnlyDormantChange={setShowOnlyDormant}
      />
    </div>
  );
}

export default App; 