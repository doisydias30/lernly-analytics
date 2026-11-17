with users as (
    select * from {{ ref('stg_users') }}
),

subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

activity as (
    select 
        user_id,
        count(*) as active_weeks
    from {{ ref('stg_weekly_activity') }}
    group by user_id
)

select
    u.user_id,
    u.signup_date,
    u.country_code,
    u.acquisition_channel,
    u.device,
    u.onboarding_variant,
    cast(date_trunc('month', u.signup_date) as date) as signup_month,
    s.plan,
    s.subscription_id is not null as has_subscribed,
    coalesce(a.active_weeks, 0) as active_weeks

from users u
left join subscriptions s
    on u.user_id = s.user_id
left join activity a
    on u.user_id = a.user_id