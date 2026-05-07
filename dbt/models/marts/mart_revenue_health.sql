with subscriptions as (
    select * from {{ ref('dim_subscriptions') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

payments as (
    select * from {{ ref('fact_payments') }}
)

select
    customers.segment,
    customers.country,
    count(distinct customers.customer_id) as customer_count,
    count(distinct subscriptions.subscription_id) as subscription_count,
    sum(subscriptions.mrr) as total_mrr,
    sum(subscriptions.is_active) as active_subscriptions,
    sum(subscriptions.is_churned) as churned_subscriptions,
    sum(customers.total_amount_invoiced) as total_amount_invoiced,
    sum(customers.total_amount_paid) as total_amount_paid,
    count(distinct payments.payment_id) as payment_count,
    avg(payments.payment_delay_days) as avg_payment_delay_days
from customers
left join subscriptions using (customer_id)
left join payments using (customer_id)
group by customers.segment, customers.country
