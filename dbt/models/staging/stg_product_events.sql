with source as (
    select *
    from read_parquet('data/bronze/product_events/*/*.parquet', union_by_name = true)
)

select
    cast(event_id as varchar) as event_id,
    cast(customer_id as varchar) as customer_id,
    cast(event_timestamp as timestamp) as event_timestamp,
    cast(event_name as varchar) as event_name,
    cast(event_count as integer) as event_count,
    cast(source as varchar) as source
from source
