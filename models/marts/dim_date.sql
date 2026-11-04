-- ============================================================
-- dim_date  (WORKED EXAMPLE)
--
-- Power BI equivalent: your Calendar table made with CALENDAR()
-- or a Power Query date list. One row per day.
-- ============================================================

with days as (

    select cast(d as date) as date_day
    from range(date '2025-01-01', date '2026-12-31' + interval 1 day, interval 1 day) as t(d)

)

select
    date_day,
    year(date_day)                                  as year,
    month(date_day)                                 as month_number,
    strftime(date_day, '%b')                        as month_name,
    cast(date_trunc('month', date_day) as date)     as month_start,
    cast(date_trunc('week', date_day) as date)      as week_start,   -- Monday
    'Q' || quarter(date_day)                        as quarter,
    isodow(date_day) in (6, 7)                      as is_weekend
from days
