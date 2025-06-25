def summary_sql(start_dt, end_dt):
    return f"""
    WITH new_users AS (
        SELECT ANONYMOUS_ID, MIN(ORIGINAL_TIMESTAMP) as first_event_date
        FROM TRACKS
        WHERE ORIGINAL_TIMESTAMP >= '{start_dt.strftime('%Y-%m-%d')}'
          AND ORIGINAL_TIMESTAMP <= '{end_dt.strftime('%Y-%m-%d')}'
        GROUP BY ANONYMOUS_ID
    ),
    activated_users AS (
        SELECT nu.ANONYMOUS_ID, CASE WHEN COUNT(t.ORIGINAL_TIMESTAMP) > 0 THEN 1 ELSE 0 END as is_activated
        FROM new_users nu
        LEFT JOIN TRACKS t ON nu.ANONYMOUS_ID = t.ANONYMOUS_ID
            AND t.ORIGINAL_TIMESTAMP BETWEEN nu.first_event_date AND DATEADD(hour, 24, nu.first_event_date)
            AND t.EVENT IN ('purchase', 'complete_registration', 'schedule')
        GROUP BY nu.ANONYMOUS_ID
    )
    SELECT COUNT(*) as total_users, SUM(is_activated) as activated_users,
           CASE WHEN COUNT(*) > 0 THEN SUM(is_activated)::FLOAT / COUNT(*)::FLOAT ELSE 0 END as activation_rate
    FROM activated_users
    """

def details_sql(start_dt, end_dt, activated_param=None):
    filter_clause = ''
    if activated_param == 'false':
        filter_clause = 'WHERE is_activated = 0'
    elif activated_param == 'true':
        filter_clause = 'WHERE is_activated = 1'
    return f"""
    WITH new_users AS (
        SELECT ANONYMOUS_ID, MIN(ORIGINAL_TIMESTAMP) as first_event_date
        FROM TRACKS
        WHERE ORIGINAL_TIMESTAMP >= '{start_dt.strftime('%Y-%m-%d')}'
          AND ORIGINAL_TIMESTAMP <= '{end_dt.strftime('%Y-%m-%d')}'
        GROUP BY ANONYMOUS_ID
    ),
    activated_users AS (
        SELECT nu.ANONYMOUS_ID, nu.first_event_date, CASE WHEN COUNT(t.ORIGINAL_TIMESTAMP) > 0 THEN 1 ELSE 0 END as is_activated, COUNT(t.ORIGINAL_TIMESTAMP) as activation_events
        FROM new_users nu
        LEFT JOIN TRACKS t ON nu.ANONYMOUS_ID = t.ANONYMOUS_ID
            AND t.ORIGINAL_TIMESTAMP BETWEEN nu.first_event_date AND DATEADD(hour, 24, nu.first_event_date)
            AND t.EVENT IN ('purchase', 'complete_registration', 'schedule')
        GROUP BY nu.ANONYMOUS_ID, nu.first_event_date
    )
    SELECT ANONYMOUS_ID as user_id, first_event_date, is_activated, activation_events,
           CASE WHEN is_activated = 1 THEN 'Activated' ELSE 'Not Activated' END as status
    FROM activated_users
    {filter_clause}
    ORDER BY first_event_date DESC
    LIMIT 100
    """ 