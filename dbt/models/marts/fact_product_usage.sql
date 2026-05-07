select
    event_id,
    customer_id,
    cast(event_timestamp as date) as event_date,
    event_timestamp,
    event_name,
    event_count,
    source
from {{ ref('stg_product_events') }}
