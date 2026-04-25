with customers as (
    select * from {{ ref('stg_customers') }}
),
transactions as (
    select * from {{ ref('stg_transactions') }}
),
summary as (
    select
        c.customer_id,
        c.name,
        c.country,
        count(t.transaction_id)                             as total_transactions,
        sum(case when t.status = 'completed' then t.amount else 0 end) as total_spent,
        max(t.created_at)                                   as last_transaction_at
    from customers c
    left join transactions t on c.customer_id = t.customer_id
    group by c.customer_id, c.name, c.country
)
select * from summary
