{#
  By default dbt names schemas like "main_staging". This small override
  makes them simply "raw", "staging" and "marts", which is easier to read.
  You don't need to change this file.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
