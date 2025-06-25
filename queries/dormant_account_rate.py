def summary_sql(start_dt, end_dt):
    return f"""
    WITH first_purchases AS (
        SELECT ANONYMOUS_ID, MIN(ORIGINAL_TIMESTAMP) as first_purchase_date
        FROM TRACKS
        WHERE EVENT = 'purchase'
          AND ORIGINAL_TIMESTAMP >= '{start_dt.strftime('%Y-%m-%d')}'
          AND ORIGINAL_TIMESTAMP <= '{end_dt.strftime('%Y-%m-%d')}'
        GROUP BY ANONYMOUS_ID
    ),
    user_sessions_after_purchase AS (
        SELECT fp.ANONYMOUS_ID, CASE WHEN COUNT(t.ORIGINAL_TIMESTAMP) = 0 THEN 1 ELSE 0 END as is_dormant
        FROM first_purchases fp
        LEFT JOIN TRACKS t ON fp.ANONYMOUS_ID = t.ANONYMOUS_ID
            AND t.ORIGINAL_TIMESTAMP > fp.first_purchase_date
        GROUP BY fp.ANONYMOUS_ID
    )
    SELECT COUNT(*) as total_users, SUM(is_dormant) as dormant_users,
           CASE WHEN COUNT(*) > 0 THEN SUM(is_dormant)::FLOAT / COUNT(*)::FLOAT ELSE 0 END as dormant_rate
    FROM user_sessions_after_purchase
    """

def details_sql(start_dt, end_dt, dormant_param=None):
    filter_clause = ''
    if dormant_param == 'true':
        filter_clause = 'WHERE is_dormant = 1'
    elif dormant_param == 'false':
        filter_clause = 'WHERE is_dormant = 0'
    return f"""
    WITH first_purchases AS (
        SELECT ANONYMOUS_ID, MIN(ORIGINAL_TIMESTAMP) as first_purchase_date
        FROM TRACKS
        WHERE EVENT = 'purchase'
          AND ORIGINAL_TIMESTAMP >= '{start_dt.strftime('%Y-%m-%d')}'
          AND ORIGINAL_TIMESTAMP <= '{end_dt.strftime('%Y-%m-%d')}'
        GROUP BY ANONYMOUS_ID
    ),
    user_sessions_after_purchase AS (
        SELECT fp.ANONYMOUS_ID, fp.first_purchase_date, CASE WHEN COUNT(t.ORIGINAL_TIMESTAMP) = 0 THEN 1 ELSE 0 END as is_dormant
        FROM first_purchases fp
        LEFT JOIN TRACKS t ON fp.ANONYMOUS_ID = t.ANONYMOUS_ID
            AND t.ORIGINAL_TIMESTAMP > fp.first_purchase_date
        GROUP BY fp.ANONYMOUS_ID, fp.first_purchase_date
    )
    SELECT ANONYMOUS_ID as user_id, first_purchase_date, is_dormant,
           CASE WHEN is_dormant = 1 THEN 'Dormant' ELSE 'Active' END as status
    FROM user_sessions_after_purchase
    {filter_clause}
    ORDER BY first_purchase_date DESC
    LIMIT 100
    """ 