"""
Metrics Service
Clean, maintainable service for calculating metrics using the registry system.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from cachetools import TTLCache, cached

from metrics_registry import registry, MetricConfig
from snowflake_service import SnowflakeService

logger = logging.getLogger(__name__)


@dataclass
class MetricResponse:
    """Standardized response for all metrics"""
    value: Optional[float]
    numerator: int
    denominator: int
    status: str
    message: str
    data: Optional[List[Dict]] = None
    cached: bool = False
    execution_time: Optional[float] = None


class MetricsService:
    """Clean service for calculating metrics"""
    
    def __init__(self):
        self.snowflake = SnowflakeService()
        self._cache = TTLCache(maxsize=100, ttl=300)  # 5 minute cache
    
    def calculate_metric(self, metric_key: str, start_dt: datetime, 
                        end_dt: datetime, **params) -> MetricResponse:
        """Calculate a single metric using the registry"""
        
        metric_config = registry.get_metric(metric_key)
        if not metric_config:
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Unknown metric: {metric_key}"
            )
        
        start_time = time.time()
        
        try:
            # Execute the summary query
            query = metric_config.summary_query_func(start_dt, end_dt)
            df = self.snowflake.execute_query(query)
            
            # Process the results based on metric type
            response = self._process_metric_results(df, metric_config, start_dt, end_dt)
            response.execution_time = time.time() - start_time
            
            logger.info(f"Calculated {metric_key} in {response.execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error calculating {metric_key}: {e}")
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="error",
                message=f"Error calculating {metric_key}: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def calculate_all_metrics(self, start_dt: datetime, 
                            end_dt: datetime) -> Dict[str, MetricResponse]:
        """Calculate all registered metrics"""
        
        metrics = {}
        all_configs = registry.get_all_metrics()
        
        for key, config in all_configs.items():
            try:
                metrics[key] = self.calculate_metric(key, start_dt, end_dt)
            except Exception as e:
                logger.error(f"Failed to calculate {key}: {e}")
                metrics[key] = MetricResponse(
                    value=None,
                    numerator=0,
                    denominator=0,
                    status="error",
                    message=f"Failed to calculate {key}: {str(e)}"
                )
        
        return metrics
    
    def get_metric_details(self, metric_key: str, start_dt: datetime, 
                          end_dt: datetime, **params) -> List[Dict]:
        """Get detailed data for a metric"""
        
        metric_config = registry.get_metric(metric_key)
        if not metric_config or not metric_config.details_query_func:
            return []
        
        try:
            # Execute the details query with parameters
            query = metric_config.details_query_func(start_dt, end_dt, **params)
            df = self.snowflake.execute_query(query)
            return self.snowflake.clean_dataframe_for_json(df)
            
        except Exception as e:
            logger.error(f"Error getting details for {metric_key}: {e}")
            return []
    
    def _process_metric_results(self, df: 'pd.DataFrame', 
                               config: MetricConfig, 
                               start_dt: datetime, 
                               end_dt: datetime) -> MetricResponse:
        """Process query results based on metric type"""
        
        if df.empty:
            return MetricResponse(
                value=None,
                numerator=0,
                denominator=0,
                status="ok",
                message=f"No data available for {config.title}",
                data=[]
            )
        
        # Get the first row (summary metrics typically return one row)
        row = df.iloc[0]
        
        # Extract values based on common column patterns
        value = self._extract_value(row, config.metric_type.value)
        numerator = self._extract_numerator(row)
        denominator = self._extract_denominator(row)
        
        # Generate message
        message = self._generate_message(config, value, numerator, denominator)
        
        # Prepare data for list/pareto metrics
        data = None
        if config.metric_type.value in ['list', 'pareto'] and len(df) > 1:
            data = self.snowflake.clean_dataframe_for_json(df)
        
        return MetricResponse(
            value=value,
            numerator=numerator,
            denominator=denominator,
            status="ok",
            message=message,
            data=data
        )
    
    def _extract_value(self, row, metric_type: str) -> Optional[float]:
        """Extract the main value from a row based on metric type"""
        
        # Common column names for different metric types
        value_columns = {
            'percentage': ['rate', 'percentage', 'ratio', 'dormant_rate', 'activation_rate'],
            'ratio': ['ratio', 'cac_to_ltv_ratio', 'value'],
            'count': ['total', 'count', 'total_leads', 'total_users'],
            'currency': ['amount', 'revenue', 'spend', 'value'],
            'list': ['event_count', 'count'],
            'pareto': ['count']
        }
        
        columns = value_columns.get(metric_type, ['value', 'total', 'count'])
        
        for col in columns:
            if col in row and row[col] is not None:
                return float(row[col])
        
        return None
    
    def _extract_numerator(self, row) -> int:
        """Extract numerator from row"""
        for col in ['numerator', 'dormant_users', 'conversions', 'total_leads']:
            if col in row and row[col] is not None:
                return int(row[col])
        return 0
    
    def _extract_denominator(self, row) -> int:
        """Extract denominator from row"""
        for col in ['denominator', 'total_users', 'total_cancels']:
            if col in row and row[col] is not None:
                return int(row[col])
        return 0
    
    def _generate_message(self, config: MetricConfig, value: Optional[float], 
                         numerator: int, denominator: int) -> str:
        """Generate a human-readable message for the metric"""
        
        if value is None:
            return f"No data available for {config.title}"
        
        if config.metric_type.value == 'percentage':
            if denominator > 0:
                return f"{numerator} out of {denominator} users ({value:.1%})"
            else:
                return f"{value:.1%} rate"
        
        elif config.metric_type.value == 'count':
            return f"{value:,.0f} total"
        
        elif config.metric_type.value == 'ratio':
            return f"{value:.2f} ratio"
        
        else:
            return config.description 