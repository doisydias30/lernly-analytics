-- ============================================================
-- stg_payments  (WORKED EXAMPLE)
--
-- Same idea as your fnParseMessyCurrency function in Power Query:
-- some amounts use a German decimal comma ("12,99"), some a dot.
-- ============================================================

with source as (

    select * from {{ ref('raw_payments') }}

),

deduplicated as (

    -- The billing export sometimes repeats a row with the same payment_id.
    select *
    from source
    qualify row_number() over (partition by payment_id order by paid_at) = 1

),

cleaned as (

    select
        payment_id,
        subscription_id,
        user_id,
        cast(paid_at as timestamp)                              as paid_at,
        cast(cast(paid_at as timestamp) as date)                as paid_date,
        cast(replace(amount_eur, ',', '.') as decimal(10, 2))   as amount_eur,
        lower(status)                                           as payment_status,

        -- A handy flag so every report counts revenue the same way.
        lower(status) = 'succeeded'                             as is_successful

    from deduplicated

)

select * from cleaned
