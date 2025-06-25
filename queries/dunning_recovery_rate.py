def summary_sql(start_dt, end_dt):
    return f"""
    WITH failed AS (
        SELECT ID AS invoice_id, CUSTOMER_ID, MIN(CREATED) AS first_failed
        FROM STRIPE.INVOICES
        WHERE STATUS = 'failed'
          AND CREATED >= '{start_dt.strftime('%Y-%m-%d')}'
          AND CREATED <= '{end_dt.strftime('%Y-%m-%d')}'
        GROUP BY ID, CUSTOMER_ID
    ),
    recovered AS (
        SELECT i.ID AS invoice_id, i.CUSTOMER_ID, i.CREATED as paid_at, c.EMAIL
        FROM STRIPE.INVOICES i
        JOIN failed f ON i.ID = f.invoice_id
        LEFT JOIN STRIPE.CUSTOMERS c ON i.CUSTOMER_ID = c.ID
        WHERE i.STATUS = 'paid'
          AND i.CREATED > f.first_failed
          AND i.CREATED >= '{start_dt.strftime('%Y-%m-%d')}'
          AND i.CREATED <= '{end_dt.strftime('%Y-%m-%d')}'
    )
    SELECT (SELECT COUNT(*) FROM recovered) as recovered, (SELECT COUNT(*) FROM failed) as failed,
           CASE WHEN (SELECT COUNT(*) FROM failed) > 0 THEN (SELECT COUNT(*) FROM recovered)::FLOAT / (SELECT COUNT(*) FROM failed)::FLOAT ELSE 0 END as dunning_recovery_rate
    """

def details_sql(start_dt, end_dt):
    return f"""
    WITH failed AS (
        SELECT ID AS invoice_id, CUSTOMER_ID, MIN(CREATED) AS first_failed
        FROM STRIPE.INVOICES
        WHERE STATUS = 'failed'
          AND CREATED >= '{start_dt.strftime('%Y-%m-%d')}'
          AND CREATED <= '{end_dt.strftime('%Y-%m-%d')}'
        GROUP BY ID, CUSTOMER_ID
    ),
    recovered AS (
        SELECT i.ID AS invoice_id, i.CUSTOMER_ID, i.CREATED as paid_at, c.EMAIL
        FROM STRIPE.INVOICES i
        JOIN failed f ON i.ID = f.invoice_id
        LEFT JOIN STRIPE.CUSTOMERS c ON i.CUSTOMER_ID = c.ID
        WHERE i.STATUS = 'paid'
          AND i.CREATED > f.first_failed
          AND i.CREATED >= '{start_dt.strftime('%Y-%m-%d')}'
          AND i.CREATED <= '{end_dt.strftime('%Y-%m-%d')}'
    )
    SELECT invoice_id, CUSTOMER_ID, paid_at, EMAIL
    FROM recovered
    ORDER BY paid_at DESC
    LIMIT 100
    """ 