"""
Facebook Metrics Queries
Handles Facebook CAC to LTV ratio and Facebook Lead Ads calculations
"""

def facebook_cac_to_ltv_summary_sql(start_dt, end_dt):
    """Calculate Facebook CAC to LTV ratio summary"""
    return f"""
    WITH facebook_spend AS (
        SELECT SUM(SPEND) as total_spend
        FROM FACEBOOKADS.INSIGHTS
        WHERE DATE_START >= '{start_dt.date()}'
        AND DATE_START <= '{end_dt.date()}'
    ),
    facebook_conversions AS (
        SELECT COUNT(DISTINCT USER_ID) as conversions
        FROM COURSECREATOR360_WEBSITE_JS_PROD.PURCHASE
        WHERE TIMESTAMP >= '{start_dt.isoformat()}'
        AND TIMESTAMP <= '{end_dt.isoformat()}'
        AND CONTEXT_CAMPAIGN_SOURCE = 'facebook'
    ),
    avg_revenue AS (
        SELECT AVG(VALUE) as avg_revenue
        FROM COURSECREATOR360_WEBSITE_JS_PROD.PURCHASE
        WHERE TIMESTAMP >= '{start_dt.isoformat()}'
        AND TIMESTAMP <= '{end_dt.isoformat()}'
    )
    SELECT 
        COALESCE(fs.total_spend, 0) as total_spend,
        COALESCE(fc.conversions, 0) as conversions,
        COALESCE(ar.avg_revenue, 0) as avg_revenue,
        CASE 
            WHEN COALESCE(fc.conversions, 0) > 0 THEN COALESCE(fs.total_spend, 0) / fc.conversions
            ELSE 0 
        END as cac,
        COALESCE(ar.avg_revenue, 0) * 12 as ltv,
        CASE 
            WHEN COALESCE(fc.conversions, 0) > 0 AND COALESCE(fs.total_spend, 0) > 0 
            THEN (COALESCE(ar.avg_revenue, 0) * 12) / (COALESCE(fs.total_spend, 0) / fc.conversions)
            ELSE 0 
        END as cac_to_ltv_ratio
    FROM facebook_spend fs
    CROSS JOIN facebook_conversions fc
    CROSS JOIN avg_revenue ar
    """

def facebook_cac_to_ltv_details_sql(start_dt, end_dt):
    """Get detailed Facebook CAC to LTV breakdown"""
    return f"""
    SELECT 
        'Facebook Ad Spend' as metric_type,
        SUM(SPEND) as value,
        'USD' as unit
    FROM FACEBOOKADS.INSIGHTS
    WHERE DATE_START >= '{start_dt.date()}'
    AND DATE_START <= '{end_dt.date()}'
    UNION ALL
    SELECT 
        'Facebook Conversions' as metric_type,
        COUNT(DISTINCT USER_ID) as value,
        'users' as unit
    FROM COURSECREATOR360_WEBSITE_JS_PROD.PURCHASE
    WHERE TIMESTAMP >= '{start_dt.isoformat()}'
    AND TIMESTAMP <= '{end_dt.isoformat()}'
    AND CONTEXT_CAMPAIGN_SOURCE = 'facebook'
    UNION ALL
    SELECT 
        'Average Revenue' as metric_type,
        AVG(VALUE) as value,
        'USD' as unit
    FROM COURSECREATOR360_WEBSITE_JS_PROD.PURCHASE
    WHERE TIMESTAMP >= '{start_dt.isoformat()}'
    AND TIMESTAMP <= '{end_dt.isoformat()}'
    """

def facebook_lead_ads_summary_sql(start_dt, end_dt):
    """Calculate Facebook Lead Ads total"""
    return f"""
    SELECT COUNT(*) as total_leads
    FROM FACEBOOK_LEAD_ADS.IDENTIFIES
    WHERE TIMESTAMP >= '{start_dt.isoformat()}'
    AND TIMESTAMP <= '{end_dt.isoformat()}'
    """

def facebook_lead_ads_details_sql(start_dt, end_dt):
    """Get detailed Facebook Lead Ads data"""
    return f"""
    SELECT 
        ID as user_id,
        TIMESTAMP,
        CAMPAIGN_NAME as campaign_name,
        'facebook_lead_ads' as source,
        EMAIL as email,
        NAME as name,
        PHONE_NUMBER as phone
    FROM FACEBOOK_LEAD_ADS.IDENTIFIES
    WHERE TIMESTAMP >= '{start_dt.isoformat()}'
    AND TIMESTAMP <= '{end_dt.isoformat()}'
    ORDER BY TIMESTAMP DESC
    LIMIT 100
    """ 