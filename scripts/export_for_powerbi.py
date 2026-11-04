"""
Exports every table in the 'marts' schema to CSV so Power BI can load it.

Run from the project root, after `dbt build`:
    python scripts/export_for_powerbi.py

Then in Power BI: Get Data -> Folder -> point at the exports/ folder
(or load each CSV individually).
"""
import os

import duckdb

os.makedirs("exports", exist_ok=True)
con = duckdb.connect("lernly.duckdb", read_only=True)

tables = [r[0] for r in con.execute(
    "select table_name from information_schema.tables where table_schema = 'marts'"
).fetchall()]

for t in tables:
    path = f"exports/{t}.csv"
    con.sql(f"copy marts.{t} to '{path}' (header, delimiter ',')")
    n = con.execute(f"select count(*) from marts.{t}").fetchone()[0]
    print(f"{path}: {n:,} rows")
