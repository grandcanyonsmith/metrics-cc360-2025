def summary_sql(start_dt, end_dt):
    return f"""
    SELECT COUNT(*) as total_cancels,
           COUNT(CASE WHEN s.STATUS = 'canceled'
                      AND s.CANCELED_AT IS NOT NULL THEN 1 END)
             as canceled_subscriptions,
           CASE WHEN COUNT(*) > 0 THEN
                COUNT(CASE WHEN s.STATUS = 'canceled'
                           AND s.CANCELED_AT IS NOT NULL THEN 1 END)::FLOAT
                / COUNT(*)::FLOAT
                ELSE 0 END as churn_rate
    FROM STRIPE.SUBSCRIPTIONS s
    WHERE s.STATUS = 'canceled'
      AND s.CANCELED_AT >= '{start_dt.strftime('%Y-%m-%d')}'
      AND s.CANCELED_AT <= '{end_dt.strftime('%Y-%m-%d')}'
    """

def details_sql(start_dt, end_dt):
    return f"""
    SELECT s.CUSTOMER_ID as customer_id,
           s.CANCELED_AT as canceled_at,
           c.EMAIL as email
    FROM STRIPE.SUBSCRIPTIONS s
    LEFT JOIN STRIPE.CUSTOMERS c
      ON s.CUSTOMER_ID = c.ID
    WHERE s.STATUS = 'canceled'
      AND s.CANCELED_AT >= '{start_dt.strftime('%Y-%m-%d')}'
      AND s.CANCELED_AT <= '{end_dt.strftime('%Y-%m-%d')}'
    ORDER BY s.CANCELED_AT DESC
    LIMIT 100
    """ 