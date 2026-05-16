with source as (
    select *
    from read_parquet(
        'data/bronze/product_events/*/*.parquet',
        hive_partitioning = true,
        union_by_name = true
    )
),

latest_partition as (
    select max(cast(run_date as date)) as run_date
    from source
)

select
    cast(event_id as varchar) as event_id,
    cast(customer_id as varchar) as customer_id,
    cast(event_timestamp as timestamp) as event_timestamp,
    cast(event_name as varchar) as event_name,
    cast(event_count as integer) as event_count,
    cast(source as varchar) as source
from source
inner join latest_partition using (run_date)
