"""
Generates the synthetic raw data for Lernly, a fictional Berlin-based
language-learning subscription app.

All data is synthetic. Run from the project root:
    python scripts/generate_data.py

It writes five CSVs into seeds/. The data is deliberately a bit messy
(mixed date formats, German decimal commas, duplicates, inconsistent labels),
because cleaning it is part of the exercise.
"""
import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

START = date(2025, 1, 1)
LAST_SIGNUP = date(2026, 10, 31)
END = date(2026, 10, 31)          # "today" for the dataset
AB_TEST_START = date(2026, 6, 1)  # onboarding experiment starts
ANDROID_BUG = (date(2026, 8, 3), date(2026, 9, 28))  # buggy Android release

N_USERS = 6000

CHANNELS = {  # clean name: (share, messy spellings)
    "paid_social": (0.30, ["Paid Social", "paid_social", "PAID SOCIAL ", "paid social"]),
    "paid_search": (0.20, ["Paid Search", "paid_search"]),
    "organic":     (0.25, ["Organic", "organic", " organic"]),
    "referral":    (0.15, ["Referral", "referral"]),
    "app_store":   (0.10, ["App Store", "app_store", "AppStore"]),
}
COUNTRIES = {  # clean code: (share, messy spellings)
    "DE": (0.45, ["DE", "de", "Germany", "Deutschland"]),
    "AT": (0.10, ["AT", "Austria"]),
    "CH": (0.08, ["CH", "Switzerland"]),
    "NL": (0.10, ["NL", "Netherlands"]),
    "FR": (0.09, ["FR", "France"]),
    "ES": (0.08, ["ES", "Spain"]),
    "IN": (0.10, ["IN", "India"]),
}
DEVICES = {"iOS": 0.45, "Android": 0.40, "Web": 0.15}

MONTHLY_PRICE, ANNUAL_PRICE = 12.99, 89.99


def pick(d):
    keys = list(d)
    probs = np.array([v[0] if isinstance(v, tuple) else v for v in d.values()])
    return np.random.choice(keys, p=probs / probs.sum())


def signup_date():
    # January spike (New Year resolutions) + gentle growth over time
    while True:
        d = START + timedelta(days=random.randint(0, (LAST_SIGNUP - START).days))
        w = 1.0 + 0.6 * (d - START).days / (LAST_SIGNUP - START).days
        if d.month == 1:
            w *= 1.8
        if random.random() < w / 2.9:
            return d


def ts(d, hour_lo=7, hour_hi=23):
    return datetime(d.year, d.month, d.day, random.randint(hour_lo, hour_hi - 1),
                    random.randint(0, 59), random.randint(0, 59))


users, events, subs, payments, activity = [], [], [], [], []
event_id = sub_id = pay_id = 0

for uid in range(1, N_USERS + 1):
    su = signup_date()
    channel = pick(CHANNELS)
    country = pick(COUNTRIES)
    device = pick(DEVICES)
    variant = None
    if su >= AB_TEST_START:
        variant = random.choice(["control", "new_flow"])

    # ---- messy user row ----
    signup_str = su.strftime("%d.%m.%Y") if random.random() < 0.15 else su.isoformat()
    country_raw = None if random.random() < 0.03 else random.choice(COUNTRIES[country][1])
    users.append({
        "user_id": f"U{uid:05d}",
        "signup_date": signup_str,
        "country": country_raw,
        "acquisition_channel": random.choice(CHANNELS[channel][1]),
        "device": device,
        "onboarding_variant": variant,
    })

    def add_event(name, d):
        global event_id
        event_id += 1
        events.append({"event_id": f"E{event_id:07d}", "user_id": f"U{uid:05d}",
                       "event_name": name, "event_at": ts(d).isoformat(sep=" ")})

    add_event("signup", su)

    # ---- funnel ----
    p_onboard = 0.62 if variant != "new_flow" else 0.70
    p_trial = {"paid_social": 0.38, "paid_search": 0.50, "organic": 0.55,
               "referral": 0.60, "app_store": 0.50}[channel]
    p_paid = 0.30 if variant != "new_flow" else 0.34
    if channel == "referral":
        p_paid += 0.05

    onboarded = random.random() < p_onboard
    trial_day = paid_day = None
    if onboarded:
        add_event("onboarding_completed", su + timedelta(days=random.choice([0, 0, 0, 1])))
        if random.random() < 0.8:
            add_event("paywall_viewed", su + timedelta(days=random.randint(0, 3)))
            if random.random() < p_trial:
                trial_day = su + timedelta(days=random.randint(0, 5))
                add_event("trial_started", trial_day)
                if random.random() < p_paid and trial_day + timedelta(days=7) <= END:
                    paid_day = trial_day + timedelta(days=7)
                    add_event("subscribed", paid_day)

    # ---- subscription + payments ----
    churn_day = None
    if paid_day:
        sub_id += 1
        plan = "annual" if random.random() < 0.28 else "monthly"
        price = ANNUAL_PRICE if plan == "annual" else MONTHLY_PRICE
        monthly_hazard = {"paid_social": 0.15, "paid_search": 0.10, "organic": 0.08,
                          "referral": 0.06, "app_store": 0.09}[channel]
        period = 365 if plan == "annual" else 30
        renew_churn = 0.35 if plan == "annual" else monthly_hazard

        bill = paid_day
        cancelled = None
        while bill <= END:
            pay_id += 1
            status = "succeeded"
            r = random.random()
            if r < 0.03:
                status = "failed"
            elif r < 0.04:
                status = "refunded"
            amount = f"{price:.2f}".replace(".", ",") if random.random() < 0.2 else f"{price:.2f}"
            payments.append({"payment_id": f"P{pay_id:06d}", "subscription_id": f"S{sub_id:05d}",
                             "user_id": f"U{uid:05d}", "paid_at": ts(bill).isoformat(sep=" "),
                             "amount_eur": amount, "status": status})
            if status == "failed":  # retry next day succeeds
                pay_id += 1
                payments.append({"payment_id": f"P{pay_id:06d}", "subscription_id": f"S{sub_id:05d}",
                                 "user_id": f"U{uid:05d}",
                                 "paid_at": ts(bill + timedelta(days=1)).isoformat(sep=" "),
                                 "amount_eur": f"{price:.2f}", "status": "succeeded"})
            if random.random() < 0.02:  # duplicate export row
                payments.append(dict(payments[-1]))
            nxt = bill + timedelta(days=period)
            if random.random() < renew_churn:
                cancelled = nxt - timedelta(days=random.randint(1, 10))
                if cancelled > END:
                    cancelled = None
                break
            bill = nxt
        churn_day = cancelled
        subs.append({"subscription_id": f"S{sub_id:05d}", "user_id": f"U{uid:05d}",
                     "plan": plan, "started_at": paid_day.isoformat(),
                     "cancelled_at": cancelled.isoformat() if cancelled else None,
                     "price_eur": price})

    # ---- weekly activity ----
    week = su - timedelta(days=su.weekday())
    base = {"paid_social": 0.55, "paid_search": 0.65, "organic": 0.72,
            "referral": 0.75, "app_store": 0.68}[channel]
    alive = True
    w = 0
    while week <= END and alive:
        subscribed_now = paid_day and week >= paid_day - timedelta(days=7) and (churn_day is None or week <= churn_day)
        p_active = base * (0.93 ** w) if not subscribed_now else 0.85
        if device == "Android" and ANDROID_BUG[0] <= week <= ANDROID_BUG[1]:
            p_active *= 0.65
        if random.random() < p_active:
            activity.append({"user_id": f"U{uid:05d}", "week_start": week.isoformat(),
                             "lessons_completed": int(np.random.poisson(4 if subscribed_now else 2)) + 1})
        # permanent drop-off for non-subscribers
        if not subscribed_now and random.random() < 0.06 + (0.04 if channel == "paid_social" else 0):
            alive = False
        week += timedelta(days=7)
        w += 1

# a few duplicated user rows from a double export
for row in random.sample(users, 25):
    users.append(dict(row))
random.shuffle(users)

out = "seeds"
pd.DataFrame(users).to_csv(f"{out}/raw_users.csv", index=False)
pd.DataFrame(events).to_csv(f"{out}/raw_events.csv", index=False)
pd.DataFrame(subs).to_csv(f"{out}/raw_subscriptions.csv", index=False)
pd.DataFrame(payments).to_csv(f"{out}/raw_payments.csv", index=False)
pd.DataFrame(activity).to_csv(f"{out}/raw_weekly_activity.csv", index=False)

for name, rows in [("users", users), ("events", events), ("subscriptions", subs),
                   ("payments", payments), ("weekly_activity", activity)]:
    print(f"raw_{name}: {len(rows):,} rows")
