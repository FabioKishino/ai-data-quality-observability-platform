with payments as (
    select * from {{ ref('stg_payments') }}
),

invoices as (
    select
        invoice_id,
        subscription_id,
        invoice_date,
        due_date,
        invoice_status
    from {{ ref('stg_invoices') }}
)

select
    payments.payment_id,
    payments.invoice_id,
    invoices.subscription_id,
    payments.customer_id,
    payments.payment_date,
    invoices.invoice_date,
    invoices.due_date,
    payments.amount_paid,
    payments.payment_method,
    payments.payment_status,
    date_diff('day', invoices.invoice_date, payments.payment_date) as payment_delay_days
from payments
left join invoices using (invoice_id)
