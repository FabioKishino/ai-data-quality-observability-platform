with customers as (
    select * from {{ ref('stg_customers') }}
),

revenue as (
    select * from {{ ref('int_customer_revenue') }}
),

usage as (
    select
        customer_id,
        count(distinct event_id) as product_event_rows,
        sum(event_count) as product_event_count,
        max(event_timestamp) as latest_product_event_at
    from {{ ref('stg_product_events') }}
    group by customer_id
)

select
    customers.customer_id,
    customers.company_name,
    customers.country,
    customers.segment,
    customers.signup_date,
    customers.acquisition_channel,
    customers.account_status,
    coalesce(revenue.invoice_count, 0) as invoice_count,
    coalesce(revenue.payment_count, 0) as payment_count,
    coalesce(revenue.total_amount_invoiced, 0) as total_amount_invoiced,
    coalesce(revenue.total_amount_paid, 0) as total_amount_paid,
    coalesce(usage.product_event_rows, 0) as product_event_rows,
    coalesce(usage.product_event_count, 0) as product_event_count,
    usage.latest_product_event_at
from customers
left join revenue using (customer_id)
left join usage using (customer_id)
