with source as (
    select *
    from read_parquet('data/bronze/invoices/*/*.parquet', union_by_name = true)
)

select
    cast(invoice_id as varchar) as invoice_id,
    cast(subscription_id as varchar) as subscription_id,
    cast(customer_id as varchar) as customer_id,
    cast(invoice_date as date) as invoice_date,
    cast(due_date as date) as due_date,
    cast(amount_due as decimal(12, 2)) as amount_due,
    cast(currency as varchar) as currency,
    cast(invoice_status as varchar) as invoice_status
from source
