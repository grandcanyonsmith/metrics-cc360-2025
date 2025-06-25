def cac_spend_query(start_date, end_date):
    """Get total Facebook ad spend for CAC calculation"""
    return f"""
    SELECT SUM(i.SPEND) AS total_spend
    FROM FACEBOOKADS.INSIGHTS i
    WHERE i.DATE_START >= '{start_date}'
      AND i.DATE_START <= '{end_date}'
    """


def cac_trials_query(start_date, end_date):
    """Get total new Stripe trials for CAC calculation, 
    including starter/premium/elite plans"""
    return f"""
    SELECT COUNT(*) AS total_trials
    FROM STRIPE.SUBSCRIPTIONS s
    LEFT JOIN STRIPE.PLANS p ON s.PLAN_ID = p.ID
    LEFT JOIN STRIPE.PRODUCTS pr ON p.PRODUCT = pr.ID
    WHERE s.TRIAL_START IS NOT NULL
      AND s.TRIAL_START >= '{start_date}'
      AND s.TRIAL_START <= '{end_date}'
      AND (
        LOWER(pr.NAME) LIKE '%starter%'
        OR LOWER(pr.NAME) LIKE '%elite%'
        OR LOWER(pr.NAME) LIKE '%premium%'
      )
    """


def included_trials_query(start_date, end_date):
    """Get all Stripe trials for starter, premium, or elite plans in the date range."""
    return f"""
    SELECT
      s.ID AS subscription_id,
      pr.NAME AS product_name,
      c.EMAIL AS customer_email,
      c.DESCRIPTION AS customer_name,
      s.TRIAL_START,
      s.START_DATE,
      s.STATUS
    FROM STRIPE.SUBSCRIPTIONS s
      JOIN STRIPE.PLANS p ON s.PLAN_ID = p.ID
      JOIN STRIPE.PRODUCTS pr ON p.PRODUCT = pr.ID
      JOIN STRIPE.CUSTOMERS c ON s.CUSTOMER_ID = c.ID
    WHERE
      s.TRIAL_START >= '{start_date}'
      AND s.TRIAL_START <= '{end_date}'
      AND (
        LOWER(pr.NAME) LIKE '%starter%'
        OR LOWER(pr.NAME) LIKE '%elite%'
        OR LOWER(pr.NAME) LIKE '%premium%'
      )
    ORDER BY s.TRIAL_START DESC
    """


    # get all stripe with this