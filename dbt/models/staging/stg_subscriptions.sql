with source as (
    select *
    from read_parquet('data/bronze/subscriptions/*/*.parquet', union_by_name = true)
)

select
    cast(subscription_id as varchar) as subscription_id,
    cast(customer_id as varchar) as customer_id,
    cast(plan_tier as varchar) as plan_tier,
    cast(billing_period as varchar) as billing_period,
    cast(started_at as date) as started_at,
    cast(canceled_at as date) as canceled_at,
    cast(mrr as decimal(12, 2)) as mrr,
    cast(subscription_status as varchar) as subscription_status
from source
