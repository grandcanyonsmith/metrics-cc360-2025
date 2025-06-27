"""
Root Cause Pareto Analysis Queries
Handles payment failure analysis and Pareto charts
"""


def root_cause_pareto_summary_sql(start_dt, end_dt):
    """Calculate root cause Pareto summary"""
    return f"""
    SELECT 
        FAILURE_CODE as reason,
        COUNT(*) as count
    FROM STRIPE.CHARGES
    WHERE CREATED >= '{start_dt.isoformat()}'
    AND CREATED <= '{end_dt.isoformat()}'
    AND STATUS = 'failed'
    AND FAILURE_CODE IS NOT NULL
    GROUP BY FAILURE_CODE
    ORDER BY count DESC
    LIMIT 5
    """


def root_cause_pareto_details_sql(start_dt, end_dt):
    """Get detailed root cause Pareto data"""
    return f"""
    SELECT 
        FAILURE_CODE as reason,
        COUNT(*) as count,
        DATE(CREATED) as date
    FROM STRIPE.CHARGES
    WHERE CREATED >= '{start_dt.isoformat()}'
    AND CREATED <= '{end_dt.isoformat()}'
    AND STATUS = 'failed'
    AND FAILURE_CODE IS NOT NULL
    GROUP BY FAILURE_CODE, DATE(CREATED)
    ORDER BY count DESC
    """ 