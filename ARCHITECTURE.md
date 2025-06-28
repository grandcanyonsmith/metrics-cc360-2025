# Clean SaaS Metrics Dashboard Architecture

## Overview

This refactored architecture makes it **much easier** to add new metrics and maintain the codebase. The system is now modular, well-organized, and follows clean code principles.

## Architecture Components

### 1. **Metrics Registry** (`metrics_registry.py`)
- **Central configuration** for all metrics
- **Single source of truth** for metric definitions
- **Easy to add new metrics** without touching main application code

### 2. **Metrics Service** (`metrics_service.py`)
- **Clean business logic** for calculating metrics
- **Standardized processing** of query results
- **Automatic error handling** and logging

### 3. **Snowflake Service** (`snowflake_service.py`)
- **Database abstraction layer**
- **Connection pooling** and management
- **Query execution** with error handling

### 4. **Main Application** (`app_clean.py`)
- **Clean API endpoints**
- **Error handling** and logging
- **Static file serving**

## How to Add a New Metric

### Step 1: Create Query File
Create a new file in `queries/` directory:

```python
# queries/my_new_metric.py

def summary_sql(start_dt, end_dt):
    return f"""
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
    return f"""
    SELECT user_id, timestamp, value, status
    FROM your_table
    WHERE timestamp >= '{start_dt.strftime('%Y-%m-%d')}'
      AND timestamp <= '{end_dt.strftime('%Y-%m-%d')}'
    ORDER BY timestamp DESC
    LIMIT 100
    """
```

### Step 2: Register the Metric
Add to `metrics_registry.py` in the `register_all_metrics()` function:

```python
from queries.my_new_metric import summary_sql as my_summary_sql, details_sql as my_details_sql

registry.register_metric(MetricConfig(
    key="my_new_metric",
    title="My New Metric",
    description="Description of what this metric measures",
    category="Marketing",  # Choose from: Marketing, Finance, Customer Success, Product & IT
    metric_type=MetricType.PERCENTAGE,  # Choose from: PERCENTAGE, COUNT, RATIO, CURRENCY, LIST, PARETO
    summary_query_func=my_summary_sql,
    details_query_func=my_details_sql,
    color="bg-blue-50 border-blue-200 text-blue-700",
    icon="Activity",
    trend="up",
    trend_value="+5.2%"
))
```

### Step 3: Done!
The metric is now automatically available in:
- Dashboard API (`/api/dashboard_metrics`)
- Details API (`/api/metric_details/my_new_metric`)
- Configuration API (`/api/metrics/config`)

## Metric Types

### 1. **PERCENTAGE**
- For metrics like conversion rates, churn rates
- Expects: `rate`, `percentage`, `ratio` columns
- Example: Dormant Account Rate, Activation Rate

### 2. **COUNT**
- For total counts and sums
- Expects: `total`, `count`, `total_leads` columns
- Example: Facebook Lead Ads Total

### 3. **RATIO**
- For ratios like CAC:LTV
- Expects: `ratio`, `cac_to_ltv_ratio` columns
- Example: Facebook CAC to LTV Ratio

### 4. **CURRENCY**
- For monetary values
- Expects: `amount`, `revenue`, `spend` columns
- Example: Monthly Revenue, Ad Spend

### 5. **LIST**
- For breakdown data
- Expects: `event_count`, `count` columns
- Example: Platform Breakdown

### 6. **PARETO**
- For Pareto analysis
- Expects: `count` column
- Example: Root Cause Pareto

## Categories

- **Customer Success**: User engagement, activation, retention
- **Finance**: Revenue, churn, payment processing
- **Marketing**: CAC, LTV, lead generation
- **Product & IT**: Platform usage, technical metrics

## API Endpoints

### Dashboard Metrics
```
GET /api/dashboard_metrics?start=2025-01-01&end=2025-01-31
```

### Metric Details
```
GET /api/metric_details/{metric_name}?start=2025-01-01&end=2025-01-31&param=value
```

### Metrics Configuration
```
GET /api/metrics/config
```

### Categories
```
GET /api/categories
```

## Benefits of New Architecture

### ✅ **Easy to Add Metrics**
- Copy template file
- Add 3 lines to registry
- Done!

### ✅ **Consistent Structure**
- All metrics follow same pattern
- Standardized error handling
- Uniform API responses

### ✅ **Maintainable**
- Clear separation of concerns
- Single responsibility principle
- Easy to test and debug

### ✅ **Scalable**
- Registry pattern for easy extension
- Service layer for business logic
- Database abstraction

### ✅ **Type Safe**
- Strong typing throughout
- Clear interfaces
- Better IDE support

## Migration Guide

To migrate from the old architecture:

1. **Backup current app.py** as `app_old.py`
2. **Replace app.py** with `app_clean.py`
3. **Test thoroughly** to ensure all metrics work
4. **Update frontend** if needed (should be compatible)

## File Structure

```
├── app_clean.py              # New main application
├── metrics_registry.py       # Central metric configuration
├── metrics_service.py        # Business logic for metrics
├── snowflake_service.py      # Database operations
├── queries/                  # SQL query files
│   ├── dormant_account_rate.py
│   ├── t24h_activation_rate.py
│   └── ...
├── templates/
│   └── new_metric_template.py  # Template for new metrics
└── ARCHITECTURE.md           # This documentation
```

## Example: Adding a New Metric

Let's say you want to add a "Monthly Active Users" metric:

1. **Create** `queries/monthly_active_users.py`:
```python
def summary_sql(start_dt, end_dt):
    return f"""
    SELECT COUNT(DISTINCT user_id) as total_users
    FROM user_events
    WHERE event_date >= '{start_dt.strftime('%Y-%m-%d')}'
      AND event_date <= '{end_dt.strftime('%Y-%m-%d')}'
    """

def details_sql(start_dt, end_dt, **params):
    return f"""
    SELECT user_id, event_date, event_type
    FROM user_events
    WHERE event_date >= '{start_dt.strftime('%Y-%m-%d')}'
      AND event_date <= '{end_dt.strftime('%Y-%m-%d')}'
    ORDER BY event_date DESC
    LIMIT 100
    """
```

2. **Add to registry** in `metrics_registry.py`:
```python
from queries.monthly_active_users import summary_sql as mau_summary_sql, details_sql as mau_details_sql

registry.register_metric(MetricConfig(
    key="monthly_active_users",
    title="Monthly Active Users",
    description="Number of unique users with activity in the selected period",
    category="Customer Success",
    metric_type=MetricType.COUNT,
    summary_query_func=mau_summary_sql,
    details_query_func=mau_details_sql,
    color="bg-green-50 border-green-200 text-green-700",
    icon="Users",
    trend="up",
    trend_value="+15%"
))
```

3. **Restart the application** - the metric is now live!

That's it! No other code changes needed. The metric will automatically appear in the dashboard, API, and frontend. 