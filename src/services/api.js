import axios from 'axios';

// Use relative paths for production deployment
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Fetch all dashboard summary metrics
export const fetchDashboardMetrics = async (startDate, endDate) => {
  try {
    const response = await api.get('/api/dashboard_metrics', {
      params: { start: startDate, end: endDate },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    throw error;
  }
};

// Micro-API functions for each metric's details
export const fetchDormantAccountRateDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('dormant_account_rate', startDate, endDate, extraParams);

export const fetchInvoluntaryChurnRateDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('involuntary_churn_rate', startDate, endDate, extraParams);

export const fetchDunningRecoveryRateDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('dunning_recovery_rate', startDate, endDate, extraParams);

export const fetchT24hActivationRateDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('t24h_activation_rate', startDate, endDate, extraParams);

export const fetchSourceAttributionCoverageDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('source_attribution_coverage', startDate, endDate, extraParams);

export const fetchPlatformBreakdownDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('platform_breakdown', startDate, endDate, extraParams);

export const fetchRootCauseParetoDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('root_cause_pareto', startDate, endDate, extraParams);

export const fetchDailyTrendsDetails = (startDate, endDate, extraParams = {}) =>
  fetchMetricDetails('daily_trends', startDate, endDate, extraParams);

// Generic fetch for metric details
export const fetchMetricDetails = async (metric, startDate, endDate, extraParams = {}) => {
  try {
    const response = await api.get('/api/dashboard_metric_rows', {
      params: { metric, start: startDate, end: endDate, ...extraParams },
    });
    return response.data.rows || [];
  } catch (error) {
    console.error(`Error fetching ${metric} details:`, error);
    throw error;
  }
};

export default api; 