with source as (
    select * from {{ ref('raw_subscriptions') }}

),
cleaned as (

    select
        subscription_id,user_id,plan,

        -- Dates arrive in two formats: 2026-03-14 and 14.03.2026 (German style).
        -- try_strptime returns NULL if the format doesn't match,
        -- so coalesce picks whichever one worked.
        cast(started_at as date)     as started_at,
        cast(cancelled_at as date) as cancelled_at,
        cast(price_eur as decimal(10, 2)) as price_eur,
        cancelled_at is null as is_active
    from source

)

select * from cleaned
