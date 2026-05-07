with subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
)

select
    subscriptions.subscription_id,
    subscriptions.customer_id,
    customers.segment,
    customers.country,
    subscriptions.plan_tier,
    subscriptions.billing_period,
    subscriptions.started_at,
    subscriptions.canceled_at,
    subscriptions.mrr,
    subscriptions.subscription_status,
    case when subscriptions.subscription_status = 'active' then 1 else 0 end as is_active,
    case when subscriptions.subscription_status = 'canceled' then 1 else 0 end as is_churned,
    date_diff('day', subscriptions.started_at, coalesce(subscriptions.canceled_at, current_date))
        as subscription_age_days
from subscriptions
left join customers using (customer_id)
