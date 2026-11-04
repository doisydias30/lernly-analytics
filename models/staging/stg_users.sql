-- ============================================================
-- stg_users  (WORKED EXAMPLE — read this one carefully)
--
-- Power BI equivalent: a Power Query that cleans the raw Users
-- table. Same steps you already do: remove duplicates, fix
-- dates, trim and standardise text. Here it's written in SQL,
-- saved as a file, and version-controlled.
--
-- Rule for staging models: ONE raw table in, ONE clean table out.
-- No joins, no business logic. Just make the data trustworthy.
-- ============================================================

with source as (

    -- ref() is how dbt points at another table.
    -- (Careful: dbt reads double-curly-brace code even inside SQL comments!)
    -- Like referencing another query in Power Query.
    -- dbt uses these refs to work out the run order automatically.
    select * from {{ ref('raw_users') }}

),

deduplicated as (

    -- The export contains some exact duplicate rows.
    -- Keep one row per user_id.
    select *
    from source
    qualify row_number() over (partition by user_id order by signup_date) = 1

),

cleaned as (

    select
        user_id,

        -- Dates arrive in two formats: 2026-03-14 and 14.03.2026 (German style).
        -- try_strptime returns NULL if the format doesn't match,
        -- so coalesce picks whichever one worked.
        cast(coalesce(
            try_strptime(signup_date, '%Y-%m-%d'),
            try_strptime(signup_date, '%d.%m.%Y')
        ) as date)                                              as signup_date,

        -- Country arrives as codes, English names and German names.
        case upper(trim(country))
            when 'DE' then 'DE' when 'GERMANY' then 'DE' when 'DEUTSCHLAND' then 'DE'
            when 'AT' then 'AT' when 'AUSTRIA' then 'AT'
            when 'CH' then 'CH' when 'SWITZERLAND' then 'CH'
            when 'NL' then 'NL' when 'NETHERLANDS' then 'NL'
            when 'FR' then 'FR' when 'FRANCE' then 'FR'
            when 'ES' then 'ES' when 'SPAIN' then 'ES'
            when 'IN' then 'IN' when 'INDIA' then 'IN'
            else 'Unknown'
        end                                                     as country_code,

        -- "PAID SOCIAL ", "paid_social", "Paid Social" -> paid_social
        replace(replace(lower(trim(acquisition_channel)), ' ', '_'), 'appstore', 'app_store')
                                                                as acquisition_channel,

        device,

        -- NULL means the user signed up before the A/B test began.
        onboarding_variant

    from deduplicated

)

select * from cleaned
