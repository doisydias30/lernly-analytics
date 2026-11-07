with source as (
    select * from {{ ref('raw_events') }}

),
cleaned as (

    select
       event_id,user_id,event_name,

        cast(event_at as timestamp) as event_at,
        cast(cast(event_at as timestamp) as date) as event_date
    from source
)

select * from cleaned
