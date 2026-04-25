select
    id              as transaction_id,
    user_id         as customer_id,
    amount,
    currency,
    status,
    created_at
from {{ source('raw', 'transactions') }}
