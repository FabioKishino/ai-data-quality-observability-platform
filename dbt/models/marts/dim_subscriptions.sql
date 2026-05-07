select
    subscription_id,
    customer_id,
    segment,
    country,
    plan_tier,
    billing_period,
    started_at,
    canceled_at,
    mrr,
    subscription_status,
    is_active,
    is_churned,
    subscription_age_days
from {{ ref('int_subscription_lifecycle') }}
