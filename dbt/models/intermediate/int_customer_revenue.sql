with invoices as (
    select * from {{ ref('stg_invoices') }}
),

payments as (
    select * from {{ ref('stg_payments') }}
),

invoice_rollup as (
    select
        customer_id,
        count(*) as invoice_count,
        sum(amount_due) as total_amount_invoiced,
        sum(case when invoice_status = 'paid' then amount_due else 0 end) as paid_invoice_amount,
        sum(case when invoice_status != 'paid' then amount_due else 0 end) as open_invoice_amount,
        min(invoice_date) as first_invoice_date,
        max(invoice_date) as latest_invoice_date
    from invoices
    group by customer_id
),

payment_rollup as (
    select
        customer_id,
        count(*) as payment_count,
        sum(amount_paid) as total_amount_paid,
        min(payment_date) as first_payment_date,
        max(payment_date) as latest_payment_date
    from payments
    group by customer_id
)

select
    coalesce(invoice_rollup.customer_id, payment_rollup.customer_id) as customer_id,
    coalesce(invoice_count, 0) as invoice_count,
    coalesce(payment_count, 0) as payment_count,
    coalesce(total_amount_invoiced, 0) as total_amount_invoiced,
    coalesce(total_amount_paid, 0) as total_amount_paid,
    coalesce(paid_invoice_amount, 0) as paid_invoice_amount,
    coalesce(open_invoice_amount, 0) as open_invoice_amount,
    first_invoice_date,
    latest_invoice_date,
    first_payment_date,
    latest_payment_date
from invoice_rollup
full outer join payment_rollup using (customer_id)
