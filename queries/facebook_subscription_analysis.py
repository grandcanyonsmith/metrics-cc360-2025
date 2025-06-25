def facebook_subscription_analysis_query():
    """Get all emails, phone numbers, and names from subscriptions containing 'starter', 'premium', or 'elite' 
    from the last 30 days, showing how many came from Facebook Lead Ads"""
    return """
    WITH facebook_leads AS (
        -- Get all Facebook Lead Ads data from last 30 days
        SELECT
            DISTINCT 
            EMAIL,
            PHONE_NUMBER,
            USER_PROVIDED_PHONE_NUMBER,
            ANONYMOUS_ID,
            TIMESTAMP
        FROM FACEBOOK_LEAD_ADS.IDENTIFIES
        WHERE TIMESTAMP >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
          AND (
            NOT EMAIL IS NULL
            OR NOT PHONE_NUMBER IS NULL
            OR NOT USER_PROVIDED_PHONE_NUMBER IS NULL
          )
    ),
    stripe_subscriptions AS (
        -- Get all Stripe subscriptions with starter/premium/elite plans from last 30 days
        SELECT
            s.ID AS subscription_id,
            s.CUSTOMER_ID,
            s.CREATED,
            s.STATUS,
            c.EMAIL AS customer_email,
            c.DESCRIPTION AS customer_name,
            pr.NAME AS product_name,
            p.AMOUNT,
            p.CURRENCY
        FROM STRIPE.SUBSCRIPTIONS s
        JOIN STRIPE.CUSTOMERS c ON s.CUSTOMER_ID = c.ID
        JOIN STRIPE.PLANS p ON s.PLAN_ID = p.ID
        JOIN STRIPE.PRODUCTS pr ON p.PRODUCT = pr.ID
        WHERE s.CREATED >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
          AND (
            LOWER(pr.NAME) LIKE '%starter%'
            OR LOWER(pr.NAME) LIKE '%elite%'
            OR LOWER(pr.NAME) LIKE '%premium%'
          )
    ),
    facebook_attributed AS (
        -- Match Facebook leads with Stripe subscriptions
        SELECT
            ss.*,
            CASE 
                WHEN fl.EMAIL IS NOT NULL OR fl.PHONE_NUMBER IS NOT NULL OR fl.USER_PROVIDED_PHONE_NUMBER IS NOT NULL 
                THEN 'Facebook Lead Ad'
                ELSE 'Other Source'
            END AS attribution_source,
            fl.EMAIL AS facebook_email,
            COALESCE(fl.PHONE_NUMBER, fl.USER_PROVIDED_PHONE_NUMBER) AS facebook_phone
        FROM stripe_subscriptions ss
        LEFT JOIN facebook_leads fl ON (
            LOWER(ss.customer_email) = LOWER(fl.EMAIL)
            OR LOWER(ss.customer_email) = LOWER(fl.USER_PROVIDED_PHONE_NUMBER)
        )
    )
    SELECT
        subscription_id,
        customer_email,
        customer_name,
        product_name,
        CREATED,
        STATUS,
        AMOUNT,
        CURRENCY,
        attribution_source,
        facebook_email,
        facebook_phone,
        CASE 
            WHEN attribution_source = 'Facebook Lead Ad' THEN 'Yes'
            ELSE 'No'
        END AS from_facebook
    FROM facebook_attributed
    ORDER BY CREATED DESC;
    """


def facebook_subscription_summary_query():
    """Get summary statistics of Facebook attribution for subscriptions"""
    return """
    WITH facebook_leads AS (
        SELECT
            DISTINCT 
            EMAIL,
            PHONE_NUMBER,
            USER_PROVIDED_PHONE_NUMBER,
            ANONYMOUS_ID,
            TIMESTAMP
        FROM FACEBOOK_LEAD_ADS.IDENTIFIES
        WHERE TIMESTAMP >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
          AND (
            NOT EMAIL IS NULL
            OR NOT PHONE_NUMBER IS NULL
            OR NOT USER_PROVIDED_PHONE_NUMBER IS NULL
          )
    ),
    stripe_subscriptions AS (
        SELECT
            s.ID AS subscription_id,
            s.CUSTOMER_ID,
            s.CREATED,
            s.STATUS,
            c.EMAIL AS customer_email,
            c.DESCRIPTION AS customer_name,
            pr.NAME AS product_name
        FROM STRIPE.SUBSCRIPTIONS s
        JOIN STRIPE.CUSTOMERS c ON s.CUSTOMER_ID = c.ID
        JOIN STRIPE.PLANS p ON s.PLAN_ID = p.ID
        JOIN STRIPE.PRODUCTS pr ON p.PRODUCT = pr.ID
        WHERE s.CREATED >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
          AND (
            LOWER(pr.NAME) LIKE '%starter%'
            OR LOWER(pr.NAME) LIKE '%elite%'
            OR LOWER(pr.NAME) LIKE '%premium%'
          )
    ),
    attribution_analysis AS (
        SELECT
            ss.*,
            CASE 
                WHEN fl.EMAIL IS NOT NULL OR fl.PHONE_NUMBER IS NOT NULL OR fl.USER_PROVIDED_PHONE_NUMBER IS NOT NULL 
                THEN 'Facebook Lead Ad'
                ELSE 'Other Source'
            END AS attribution_source
        FROM stripe_subscriptions ss
        LEFT JOIN facebook_leads fl ON (
            LOWER(ss.customer_email) = LOWER(fl.EMAIL)
            OR LOWER(ss.customer_email) = LOWER(fl.USER_PROVIDED_PHONE_NUMBER)
        )
    )
    SELECT
        COUNT(*) AS total_subscriptions,
        COUNT(CASE WHEN attribution_source = 'Facebook Lead Ad' THEN 1 END) AS from_facebook,
        COUNT(CASE WHEN attribution_source = 'Other Source' THEN 1 END) AS from_other_sources,
        ROUND(
            COUNT(CASE WHEN attribution_source = 'Facebook Lead Ad' THEN 1 END) * 100.0 / COUNT(*), 
            2
        ) AS facebook_percentage
    FROM attribution_analysis;
    """ 