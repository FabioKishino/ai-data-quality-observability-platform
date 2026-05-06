with source as (
    select *
    from read_parquet('data/bronze/customers/*/*.parquet', union_by_name = true)
)

select
    cast(customer_id as varchar) as customer_id,
    cast(company_name as varchar) as company_name,
    cast(country as varchar) as country,
    cast(segment as varchar) as segment,
    cast(signup_date as date) as signup_date,
    cast(acquisition_channel as varchar) as acquisition_channel,
    cast(account_status as varchar) as account_status
from source
