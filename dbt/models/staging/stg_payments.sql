with source as (
    select *
    from read_parquet(
        'data/bronze/payments/*/*.parquet',
        hive_partitioning = true,
        union_by_name = true
    )
),

latest_partition as (
    select max(cast(run_date as date)) as run_date
    from source
)

select
    cast(payment_id as varchar) as payment_id,
    cast(invoice_id as varchar) as invoice_id,
    cast(customer_id as varchar) as customer_id,
    cast(payment_date as date) as payment_date,
    cast(amount_paid as decimal(12, 2)) as amount_paid,
    cast(payment_method as varchar) as payment_method,
    cast(payment_status as varchar) as payment_status
from source
inner join latest_partition using (run_date)
