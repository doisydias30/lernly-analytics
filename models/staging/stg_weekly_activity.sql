with source as (

    select * from {{ ref('raw_weekly_activity') }}

),

cleaned as (

    select
        user_id || '-' || week_start    as activity_id,
        user_id,
        cast(week_start as date)        as week_start,
        lessons_completed

    from source

)

select * from cleaned