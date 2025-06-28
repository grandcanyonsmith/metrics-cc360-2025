"""
Template for adding new metrics
Copy this file and modify it to create a new metric.
"""

def summary_sql(start_dt, end_dt):
    """
    Summary query for the metric.
    Should return one row with the main metric value and supporting data.
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
    
    Returns:
        SQL query string
    """
    return f"""
    -- Your summary query here
    -- Should return columns like: value, numerator, denominator, rate, etc.
    SELECT 
        COUNT(*) as total_count,
        SUM(CASE WHEN condition THEN 1 ELSE 0 END) as numerator,
        COUNT(*) as denominator,
        CASE 
            WHEN COUNT(*) > 0 
            THEN SUM(CASE WHEN condition THEN 1 ELSE 0 END)::FLOAT / COUNT(*)::FLOAT 
            ELSE 0 
        END as rate
    FROM your_table
    WHERE timestamp >= '{start_dt.strftime('%Y-%m-%d')}'
      AND timestamp <= '{end_dt.strftime('%Y-%m-%d')}'
    """


def details_sql(start_dt, end_dt, **params):
    """
    Details query for the metric.
    Should return multiple rows with detailed breakdown.
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
        **params: Additional parameters (e.g., filters)
    
    Returns:
        SQL query string
    """
    # Handle optional parameters
    filter_clause = ''
    if params.get('some_filter') == 'true':
        filter_clause = 'WHERE some_column = true'
    
    return f"""
    -- Your details query here
    -- Should return detailed breakdown data
    SELECT 
        user_id,
        timestamp,
        value,
        category,
        status
    FROM your_table
    WHERE timestamp >= '{start_dt.strftime('%Y-%m-%d')}'
      AND timestamp <= '{end_dt.strftime('%Y-%m-%d')}'
    {filter_clause}
    ORDER BY timestamp DESC
    LIMIT 100
    """


# Example usage in metrics_registry.py:
"""
# Add this to the register_all_metrics() function in metrics_registry.py

from queries.your_new_metric import summary_sql as your_summary_sql, details_sql as your_details_sql

registry.register_metric(MetricConfig(
    key="your_new_metric",
    title="Your New Metric",
    description="Description of what this metric measures",
    category="Your Category",  # e.g., "Marketing", "Finance", "Customer Success"
    metric_type=MetricType.PERCENTAGE,  # or COUNT, RATIO, CURRENCY, LIST, PARETO
    summary_query_func=your_summary_sql,
    details_query_func=your_details_sql,
    color="bg-blue-50 border-blue-200 text-blue-700",  # Tailwind CSS classes
    icon="Activity",  # Lucide icon name
    trend="up",  # "up", "down", or None
    trend_value="+5.2%",  # Trend value or None
    requires_params=False,  # True if details query needs parameters
    param_options=None  # Dict of parameter options if requires_params=True
))
""" 