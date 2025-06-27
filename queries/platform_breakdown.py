"""
Platform Breakdown Queries
Handles platform analysis and device type breakdowns
"""


def platform_breakdown_summary_sql(start_dt, end_dt):
    """Calculate platform breakdown summary"""
    return f"""
    SELECT 
        CONTEXT_USER_AGENT_DATA_PLATFORM as platform,
        COUNT(*) as event_count,
        COUNT(DISTINCT USER_ID) as unique_users
    FROM COURSECREATOR360_WEBSITE_JS_PROD.PAGE_VIEW
    WHERE TIMESTAMP >= '{start_dt.isoformat()}'
    AND TIMESTAMP <= '{end_dt.isoformat()}'
    AND CONTEXT_USER_AGENT_DATA_PLATFORM IS NOT NULL
    GROUP BY CONTEXT_USER_AGENT_DATA_PLATFORM
    ORDER BY event_count DESC
    LIMIT 5
    """


def platform_breakdown_details_sql(start_dt, end_dt):
    """Get detailed platform breakdown data"""
    return f"""
    SELECT 
        CONTEXT_USER_AGENT_DATA_PLATFORM as platform,
        COUNT(*) as event_count,
        COUNT(DISTINCT USER_ID) as unique_users,
        DATE(TIMESTAMP) as date
    FROM COURSECREATOR360_WEBSITE_JS_PROD.PAGE_VIEW
    WHERE TIMESTAMP >= '{start_dt.isoformat()}'
    AND TIMESTAMP <= '{end_dt.isoformat()}'
    AND CONTEXT_USER_AGENT_DATA_PLATFORM IS NOT NULL
    GROUP BY CONTEXT_USER_AGENT_DATA_PLATFORM, DATE(TIMESTAMP)
    ORDER BY event_count DESC
    """ 