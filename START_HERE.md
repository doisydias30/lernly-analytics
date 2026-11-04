# Start here: your Lernly analytics project

This is your November portfolio project. By Nov 30 it will be a public GitHub
repo showing what Berlin startups ask for: **SQL + dbt data modeling, product
analytics, a dashboard, and a short A/B test analysis.**

You don't know dbt yet. That's fine: you already know 80% of it under
different names. Read section 2 before anything else.

---

## 1. The scenario

**Lernly** is a fictional Berlin startup: a language-learning app with a
7-day free trial, then a monthly (€12.99) or annual (€89.99) plan.
Users come from 5 channels, use iOS, Android or Web, and live in 7 countries.
The data runs from January 2025 to October 2026.

You've just joined as their first Data Analyst. The Head of Growth sends you this:

> Hi! Welcome aboard. Our data is a mess of CSV exports and nobody trusts
> the numbers. Could you:
> 1. Build us a clean, reliable data model we can all use.
> 2. Tell us how our funnel looks, from signup to paying subscriber.
> 3. Tell us which acquisition channels bring users who actually *stay*.
>    We spend most of our budget on paid social.
> 4. We launched a new onboarding flow as an A/B test on 1 June.
>    Did it work? Should we roll it out to everyone?
> 5. Anything in retention or engagement that worries you?
>
> A dashboard I can check weekly would be amazing.

That message *is* your project brief. Your final README answers these five
points. The data contains real answers to find. I haven't told you what they
are; finding them is the job.

---

## 2. dbt explained in Power BI terms

| dbt | What you already know in Power BI |
|---|---|
| **Seed** (a CSV in `seeds/`) | Get Data → Text/CSV |
| **Staging model** (`stg_*.sql`) | A Power Query that cleans one source table |
| **`ref('stg_users')`** | Referencing another query in Power Query |
| **Mart model** (`dim_*`, `fct_*`) | The final tables in your star schema |
| **Test** (in a `.yml` file) | A check you'd normally do by eye: "is this ID really unique?" |
| **`dbt build`** | Refresh All, plus automatic data-quality checks |
| **Lineage graph** (`dbt docs`) | Model view, but for the whole pipeline |

The big difference: everything is a **text file**. That means it goes on
GitHub, anyone can review it, and the logic is the same every run. That is
exactly why Berlin startups like it.

**A model is just one `select` statement saved in a `.sql` file.** The file
name becomes the table name. That's genuinely most of dbt.

---

## 3. Setup (about 30 minutes, Windows)

1. **Install Python 3.11 or 3.12** from python.org. On the first installer
   screen, tick **"Add Python to PATH"**.
2. **Install VS Code** if you haven't already.
3. Unzip this folder somewhere simple, like `C:\projects\lernly-analytics`.
4. Open the folder in VS Code, then open a terminal (Terminal → New Terminal) and run:

```
python -m venv .venv
.venv\Scripts\activate
pip install dbt-duckdb
dbt debug
```

`dbt debug` should end with **"All checks passed!"**

5. Build everything:

```
dbt build
```

You should see `PASS=20 ... ERROR=0`. That loaded the raw CSVs, built the
example models, and ran 20 data-quality tests.

6. Look at the data in DuckDB's browser UI (optional but nice):

```
pip install duckdb
duckdb -ui lernly.duckdb
```

If that command isn't recognised, skip it; the export script below is enough.

> **Every time you open a new terminal**, run `.venv\Scripts\activate` first.

---

## 4. Tour of the project

```
seeds/            raw CSV exports (messy on purpose: don't edit them)
models/staging/   one cleaning model per raw table
models/marts/     your star schema: dim_ and fct_ tables
analyses/         SQL for answering the brief (funnel, retention...)
scripts/          data generator + export-to-CSV for Power BI
dbt_project.yml   project settings
profiles.yml      database connection (a local DuckDB file)
```

**Already done for you, as worked examples:**
- `stg_users.sql`: removes duplicates, parses two date formats, standardises
  country and channel labels
- `stg_payments.sql`: removes duplicates, converts "12,99" to 12.99
- `dim_date.sql`: calendar table
- `_staging.yml`: tests for those two models

Read `stg_users.sql` line by line before you write anything. Every model you
write will follow the same pattern: `source → fix → select`.

---

## 5. Your exercises

### Week 1 (Nov 2–8): Setup + first models
- [ ] Setup done, `dbt build` passes
- [ ] Create a GitHub account (if needed) and an empty public repo called `lernly-analytics`
- [ ] Push this project to it (commands in section 6)
- [ ] Open each CSV in `seeds/` and write down what's messy in each one
- [ ] Write **`stg_subscriptions.sql`**: one row per subscription; proper
      dates; price as a number; add `is_active` (true when `cancelled_at` is null)
- [ ] Write **`stg_events.sql`**: event timestamp as a timestamp, plus an `event_date` column
- [ ] Write **`stg_weekly_activity.sql`**: `week_start` as a date
- [ ] Add tests for all three to `_staging.yml`, and run `dbt build` until it's green
- [ ] Commit and push

### Week 2 (Nov 9–15): The star schema (lighter week on purpose)
- [ ] **`dim_users`**: one row per user from `stg_users`, plus a few useful
      columns from other tables: did they ever subscribe? which plan?
      first subscription date?
- [ ] **`fct_payments`**: one row per payment, with `user_id` and the date key
- [ ] **`fct_subscriptions`**: one row per subscription, with lifetime in days
      and lifetime revenue (sum of *successful* payments)
- [ ] **`fct_weekly_activity`**: one row per user per active week, plus
      `weeks_since_signup` (you'll need this for retention)
- [ ] Tests for each one in `_marts.yml`
- [ ] Run `dbt docs generate` then `dbt docs serve` and look at your lineage graph.
      Take a screenshot: it goes in your README.

### Week 3 (Nov 16–22): Answer the brief
- [ ] `analyses/funnel.sql`: signup → onboarding → paywall → trial → subscribed, with conversion % at each step
- [ ] `analyses/retention_by_channel.sql`: of users who signed up in a month,
      what share were still active 4 / 8 / 12 weeks later, split by channel
- [ ] A/B test notebook (`notebooks/ab_test.ipynb`, using pandas):
      compare control vs new_flow on onboarding rate **and** subscription rate,
      and check whether each difference is statistically significant
      (a two-proportion z-test; `statsmodels` has one)
- [ ] Power BI dashboard on the marts (run `python scripts/export_for_powerbi.py`
      first): funnel, retention, revenue, A/B result
- [ ] **Start applying this week**

### Week 4 (Nov 23–30): Package it
- [ ] Fill in `README.md`: the answers to the brief, with numbers
- [ ] Add dashboard screenshots and the lineage graph to the README
- [ ] Practise the 2-minute walkthrough out loud: problem → model → findings → recommendation

### Useful DuckDB SQL you'll need
- `date_trunc('month', some_date)`: first day of the month
- `datediff('week', start_date, end_date)`: whole weeks between two dates
- `count(*) filter (where condition)`: count only some rows
- `qualify row_number() over (...) = 1`: keep one row per group (see `stg_users`)

---

## 6. Git, the minimum you need

First time (GitHub shows these commands after you create the repo):
```
git init
git add .
git commit -m "Initial Lernly dbt project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/lernly-analytics.git
git push -u origin main
```

After that, every time you finish something:
```
git add .
git commit -m "Add stg_subscriptions with tests"
git push
```

Small commits with clear messages look professional. Recruiters do open them.

---

## 7. When you get stuck

Paste the dbt error into our chat. dbt errors look scary but usually point at
the exact line. Ask for a **hint**, not the answer: you need to be able to
explain every line of this project in an interview, and you can only do that
if you wrote it.

The data is synthetic (generated by `scripts/generate_data.py`). Say so in
your README; that's normal and honest for portfolio projects.
