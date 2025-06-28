"""
Metrics Registry
Central configuration for all metrics in the dashboard.
This makes it easy to add new metrics without touching the main application code.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    COUNT = "count"
    CURRENCY = "currency"
    LIST = "list"
    PARETO = "pareto"

@dataclass
class MetricConfig:
    """Configuration for a single metric"""
    key: str
    title: str
    description: str
    category: str
    metric_type: MetricType
    summary_query_func: Callable
    details_query_func: Optional[Callable] = None
    color: str = "bg-blue-50 border-blue-200 text-blue-700"
    icon: str = "Activity"
    trend: Optional[str] = None
    trend_value: Optional[str] = None
    cache_ttl: int = 300  # 5 minutes
    requires_params: bool = False
    param_options: Optional[Dict[str, Any]] = None

class MetricsRegistry:
    """Central registry for all metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, MetricConfig] = {}
        self._categories: set = set()
    
    def register_metric(self, config: MetricConfig):
        """Register a new metric"""
        self._metrics[config.key] = config
        self._categories.add(config.category)
        logger.info(f"Registered metric: {config.key}")
    
    def get_metric(self, key: str) -> Optional[MetricConfig]:
        """Get a metric by key"""
        return self._metrics.get(key)
    
    def get_all_metrics(self) -> Dict[str, MetricConfig]:
        """Get all registered metrics"""
        return self._metrics.copy()
    
    def get_categories(self) -> list:
        """Get all categories"""
        return sorted(list(self._categories))
    
    def get_metrics_by_category(self, category: str) -> Dict[str, MetricConfig]:
        """Get all metrics in a category"""
        return {k: v for k, v in self._metrics.items() if v.category == category}

# Global registry instance
registry = MetricsRegistry()

# Import query modules
from queries.dormant_account_rate import summary_sql as dormant_summary_sql, details_sql as dormant_details_sql
from queries.t24h_activation_rate import summary_sql as t24h_summary_sql, details_sql as t24h_details_sql
from queries.involuntary_churn_rate import summary_sql as churn_summary_sql, details_sql as churn_details_sql
from queries.dunning_recovery_rate import summary_sql as dunning_summary_sql, details_sql as dunning_details_sql
from queries.facebook_metrics import (
    facebook_cac_to_ltv_summary_sql, facebook_cac_to_ltv_details_sql,
    facebook_lead_ads_summary_sql, facebook_lead_ads_details_sql
)
from queries.platform_breakdown import platform_breakdown_summary_sql as platform_summary_sql, platform_breakdown_details_sql as platform_details_sql
from queries.root_cause_pareto import root_cause_pareto_summary_sql as pareto_summary_sql, root_cause_pareto_details_sql as pareto_details_sql

# Register all metrics
def register_all_metrics():
    """Register all metrics in the system"""
    
    # Customer Success Metrics
    registry.register_metric(MetricConfig(
        key="dormant_account_rate",
        title="Dormant Account Rate",
        description="Percentage of new purchasers with zero sessions after first purchase",
        category="Customer Success",
        metric_type=MetricType.PERCENTAGE,
        summary_query_func=dormant_summary_sql,
        details_query_func=dormant_details_sql,
        color="bg-red-50 border-red-200 text-red-700",
        icon="Users",
        trend="down",
        trend_value="-2.3%",
        requires_params=True,
        param_options={"dormant": ["true", "false"]}
    ))
    
    registry.register_metric(MetricConfig(
        key="t24h_activation_rate",
        title="24h Activation Rate",
        description="Percentage of new users who performed a key action within 24 hours",
        category="Customer Success",
        metric_type=MetricType.PERCENTAGE,
        summary_query_func=t24h_summary_sql,
        details_query_func=t24h_details_sql,
        color="bg-blue-50 border-blue-200 text-blue-700",
        icon="Target",
        trend="up",
        trend_value="+3.8%",
        requires_params=True,
        param_options={"activated": ["true", "false"]}
    ))
    
    # Finance Metrics
    registry.register_metric(MetricConfig(
        key="involuntary_churn_rate",
        title="Involuntary Churn Rate",
        description="Percentage of subscriptions canceled due to failed payments",
        category="Finance",
        metric_type=MetricType.PERCENTAGE,
        summary_query_func=churn_summary_sql,
        details_query_func=churn_details_sql,
        color="bg-orange-50 border-orange-200 text-orange-700",
        icon="CreditCard",
        trend="up",
        trend_value="+1.1%"
    ))
    
    registry.register_metric(MetricConfig(
        key="dunning_recovery_rate",
        title="Dunning Recovery Rate",
        description="Percentage of failed payments that were successfully recovered",
        category="Finance",
        metric_type=MetricType.PERCENTAGE,
        summary_query_func=dunning_summary_sql,
        details_query_func=dunning_details_sql,
        color="bg-green-50 border-green-200 text-green-700",
        icon="AlertTriangle",
        trend="up",
        trend_value="+5.2%"
    ))
    
    # Marketing Metrics
    registry.register_metric(MetricConfig(
        key="facebook_cac_to_ltv_ratio",
        title="Facebook CAC to LTV Ratio",
        description="Customer Acquisition Cost to Lifetime Value ratio for Facebook ads",
        category="Marketing",
        metric_type=MetricType.RATIO,
        summary_query_func=facebook_cac_to_ltv_summary_sql,
        details_query_func=facebook_cac_to_ltv_details_sql,
        color="bg-purple-50 border-purple-200 text-purple-700",
        icon="TrendingUp",
        trend="up",
        trend_value="+0.2"
    ))
    
    registry.register_metric(MetricConfig(
        key="facebook_lead_ads_total",
        title="Facebook Lead Ads Total",
        description="Total count of Facebook lead ads in the selected date range",
        category="Marketing",
        metric_type=MetricType.COUNT,
        summary_query_func=facebook_lead_ads_summary_sql,
        details_query_func=facebook_lead_ads_details_sql,
        color="bg-pink-50 border-pink-200 text-pink-700",
        icon="DollarSign",
        trend="up",
        trend_value="+12%"
    ))
    
    # Product & IT Metrics
    registry.register_metric(MetricConfig(
        key="platform_breakdown",
        title="Platform Breakdown",
        description="Top platforms by event count",
        category="Product & IT",
        metric_type=MetricType.LIST,
        summary_query_func=platform_summary_sql,
        details_query_func=platform_details_sql,
        color="bg-gray-50 border-gray-200 text-gray-700",
        icon="Monitor"
    ))
    
    registry.register_metric(MetricConfig(
        key="root_cause_pareto",
        title="Root Cause Pareto",
        description="Top payment failure reasons",
        category="Finance",
        metric_type=MetricType.PARETO,
        summary_query_func=pareto_summary_sql,
        details_query_func=pareto_details_sql,
        color="bg-rose-50 border-rose-200 text-rose-700",
        icon="Activity"
    ))

# Initialize the registry
register_all_metrics() 