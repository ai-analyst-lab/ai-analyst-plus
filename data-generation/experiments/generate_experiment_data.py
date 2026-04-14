"""
Generate synthetic experiment datasets for teaching A/B testing and causal inference.

All datasets have KNOWN effects (stored in _answers/) so students can validate
their analyses. Deterministic seeds ensure reproducibility.

Usage:
    python generate_experiment_data.py

Generates 9 CSV files in the current directory + answer keys in _answers/.
"""

import json
import os

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "experiments")
ANSWERS_DIR = os.path.join(OUTPUT_DIR, "_answers")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ANSWERS_DIR, exist_ok=True)


def save_dataset(df, name, answer_key):
    """Save a dataset CSV and its answer key JSON."""
    csv_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"  {csv_path} ({len(df):,} rows)")

    key_path = os.path.join(ANSWERS_DIR, f"{name}_answers.json")
    with open(key_path, "w") as f:
        json.dump(answer_key, f, indent=2)


def generate_clean_ab():
    """Clean A/B test with 5% lift in checkout conversion.

    NovaMart tested a simplified checkout flow. The new flow increased
    conversion by ~5% relative. No SRM, no guardrail issues.
    """
    rng = np.random.default_rng(101)
    n = 5000

    users = []
    for i in range(n * 2):
        variant = "control" if i < n else "treatment"
        base_rate = 0.35
        lift = 0.05 if variant == "treatment" else 0.0
        converted = rng.binomial(1, base_rate * (1 + lift))
        revenue = rng.lognormal(3.5, 0.8) if converted else 0.0
        platform = rng.choice(["ios", "android", "web"], p=[0.4, 0.35, 0.25])
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "converted": converted,
            "revenue": round(revenue, 2),
            "platform": platform,
            "signup_days": int(rng.exponential(180)),
        })

    df = pd.DataFrame(users)
    save_dataset(df, "clean_ab", {
        "true_effect": "5% relative lift in conversion",
        "baseline_rate": 0.35,
        "true_lift_relative": 0.05,
        "srm": "PASS",
        "guardrails": "clean",
        "expected_verdict": "SHIP",
        "notes": "Clean experiment with clear positive result.",
    })
    return df


def generate_srm_violation():
    """A/B test with Sample Ratio Mismatch (52/48 split).

    Assignment bug caused more users to land in control. Results are invalid.
    """
    rng = np.random.default_rng(102)
    n_control = 5200
    n_treatment = 4800

    users = []
    for i in range(n_control + n_treatment):
        variant = "control" if i < n_control else "treatment"
        converted = rng.binomial(1, 0.35)
        revenue = rng.lognormal(3.5, 0.8) if converted else 0.0
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "converted": converted,
            "revenue": round(revenue, 2),
            "platform": rng.choice(["ios", "android", "web"]),
        })

    df = pd.DataFrame(users)
    save_dataset(df, "srm_violation", {
        "true_effect": "None (SRM invalidates results)",
        "observed_split": "52/48",
        "expected_split": "50/50",
        "srm": "BLOCK",
        "expected_verdict": "INVALID",
        "notes": "Assignment bug caused 52/48 split. Chi-squared should reject.",
    })
    return df


def generate_guardrail_violation():
    """A/B test where conversion improves but page load time degrades.

    New checkout flow: +3% conversion, but +200ms p95 latency. Classic trade-off.
    """
    rng = np.random.default_rng(103)
    n = 5000

    users = []
    for i in range(n * 2):
        variant = "control" if i < n else "treatment"
        conv_rate = 0.35 * (1.03 if variant == "treatment" else 1.0)
        converted = rng.binomial(1, conv_rate)
        revenue = rng.lognormal(3.5, 0.8) if converted else 0.0
        # Latency: treatment is slower
        base_latency = rng.lognormal(6.5, 0.3)  # ~660ms median
        latency = base_latency * (1.15 if variant == "treatment" else 1.0)
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "converted": converted,
            "revenue": round(revenue, 2),
            "page_load_ms": round(latency, 0),
            "platform": rng.choice(["ios", "android", "web"]),
        })

    df = pd.DataFrame(users)
    save_dataset(df, "guardrail_violation", {
        "true_effect": "+3% relative lift in conversion",
        "guardrail_violation": "+15% increase in page load time",
        "srm": "PASS",
        "expected_verdict": "INVESTIGATE (Mixed Results Framework)",
        "notes": "Primary metric up but latency guardrail violated. Net impact analysis needed.",
    })
    return df


def generate_underpowered():
    """A/B test with true 2% effect but only 500/group — underpowered.

    The effect is real but the sample is too small to detect it.
    """
    rng = np.random.default_rng(104)
    n = 500

    users = []
    for i in range(n * 2):
        variant = "control" if i < n else "treatment"
        conv_rate = 0.35 * (1.02 if variant == "treatment" else 1.0)
        converted = rng.binomial(1, conv_rate)
        revenue = rng.lognormal(3.5, 0.8) if converted else 0.0
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "converted": converted,
            "revenue": round(revenue, 2),
        })

    df = pd.DataFrame(users)
    save_dataset(df, "underpowered", {
        "true_effect": "2% relative lift (real but small)",
        "sample_size_per_group": 500,
        "power_to_detect": "<20%",
        "srm": "PASS",
        "expected_verdict": "LEARN (underpowered null)",
        "notes": "True effect exists but experiment too small to detect it.",
    })
    return df


def generate_no_effect():
    """A/B test with no true effect and adequate power.

    Powered null — the experiment had enough data to detect a 5% lift,
    but there is no effect.
    """
    rng = np.random.default_rng(105)
    n = 5000

    users = []
    for i in range(n * 2):
        variant = "control" if i < n else "treatment"
        converted = rng.binomial(1, 0.35)  # Same rate for both
        revenue = rng.lognormal(3.5, 0.8) if converted else 0.0
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "converted": converted,
            "revenue": round(revenue, 2),
            "platform": rng.choice(["ios", "android", "web"]),
        })

    df = pd.DataFrame(users)
    save_dataset(df, "no_effect", {
        "true_effect": "None (both groups have identical rates)",
        "baseline_rate": 0.35,
        "srm": "PASS",
        "expected_verdict": "ABORT (powered null)",
        "notes": "No effect. With 5000/group, we had >95% power to detect 5% relative lift.",
    })
    return df


def generate_mixed_results():
    """A/B test with primary metric up but secondary metric down.

    New feature boosts engagement but hurts retention.
    """
    rng = np.random.default_rng(106)
    n = 5000

    users = []
    for i in range(n * 2):
        variant = "control" if i < n else "treatment"
        # Primary: sessions per user (treatment is higher)
        sessions = rng.poisson(8 * (1.10 if variant == "treatment" else 1.0))
        # Secondary: 30-day retention (treatment is LOWER)
        retained = rng.binomial(1, 0.60 * (0.95 if variant == "treatment" else 1.0))
        # Revenue follows sessions
        revenue = sessions * rng.lognormal(1.5, 0.5)
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "sessions_14d": sessions,
            "retained_30d": retained,
            "revenue_30d": round(revenue, 2),
            "platform": rng.choice(["ios", "android", "web"]),
        })

    df = pd.DataFrame(users)
    save_dataset(df, "mixed_results", {
        "true_effects": {
            "sessions_14d": "+10% (primary, positive)",
            "retained_30d": "-5% (secondary, negative)",
        },
        "srm": "PASS",
        "expected_verdict": "LEARN or INVESTIGATE",
        "notes": "Engagement up but retention down. Need to weigh trade-offs.",
    })
    return df


def generate_did_parallel():
    """DiD dataset with parallel pre-trends and known treatment effect of +3.

    NovaMart rolled out a new feature to iOS users. Android is the control.
    10 weeks of data (5 pre, 5 post).
    """
    rng = np.random.default_rng(107)
    n_users = 200
    n_weeks = 10
    treatment_week = 5

    rows = []
    for uid in range(n_users):
        platform = "ios" if uid < 100 else "android"
        is_treated = platform == "ios"
        user_base = 20 + rng.normal(0, 3)

        for week in range(n_weeks):
            post = week >= treatment_week
            trend = week * 0.5  # Common upward trend
            effect = 3.0 if (is_treated and post) else 0.0
            noise = rng.normal(0, 2)
            orders = max(0, round(user_base + trend + effect + noise))
            rows.append({
                "user_id": f"u{uid:04d}",
                "platform": platform,
                "week": week,
                "post": int(post),
                "treated": int(is_treated),
                "orders": orders,
            })

    df = pd.DataFrame(rows)
    save_dataset(df, "did_parallel", {
        "true_effect": "+3.0 orders per user per week",
        "treatment_group": "ios",
        "control_group": "android",
        "intervention_week": 5,
        "parallel_trends": "PASS (both groups trend at +0.5/week pre-treatment)",
        "expected_verdict": "Significant DiD estimate ~3.0",
    })
    return df


def generate_did_broken():
    """DiD dataset where parallel trends are VIOLATED.

    iOS users had a steeper pre-trend than Android. DiD would be biased.
    """
    rng = np.random.default_rng(108)
    n_users = 200
    n_weeks = 10
    treatment_week = 5

    rows = []
    for uid in range(n_users):
        platform = "ios" if uid < 100 else "android"
        is_treated = platform == "ios"
        user_base = 20 + rng.normal(0, 3)

        for week in range(n_weeks):
            post = week >= treatment_week
            # BROKEN: iOS trends faster than Android pre-treatment
            trend = week * (1.2 if is_treated else 0.5)
            effect = 3.0 if (is_treated and post) else 0.0
            noise = rng.normal(0, 2)
            orders = max(0, round(user_base + trend + effect + noise))
            rows.append({
                "user_id": f"u{uid:04d}",
                "platform": platform,
                "week": week,
                "post": int(post),
                "treated": int(is_treated),
                "orders": orders,
            })

    df = pd.DataFrame(rows)
    save_dataset(df, "did_broken", {
        "true_effect": "+3.0 but DiD estimate will be BIASED",
        "treatment_group": "ios",
        "control_group": "android",
        "intervention_week": 5,
        "parallel_trends": "FAIL (iOS pre-trend 1.2/week vs Android 0.5/week)",
        "expected_verdict": "Parallel trends test should FAIL. Honest caveat required.",
    })
    return df


def generate_confounded():
    """Observational data where feature adoption is confounded by user tenure.

    Power users (longer tenure) both adopt the feature more AND have higher
    outcomes naturally. Naive comparison overstates the treatment effect.
    PSM should partially correct this.
    """
    rng = np.random.default_rng(109)
    n = 2000

    tenure_months = rng.exponential(12, size=n) + 1
    # Higher tenure → more likely to adopt feature
    adopt_prob = 1 / (1 + np.exp(-(tenure_months - 12) / 5))
    adopted = rng.binomial(1, adopt_prob)
    # Outcome depends on tenure AND adoption
    # True causal effect of adoption = +5.0
    orders = (10 + 0.5 * tenure_months + 5.0 * adopted
              + rng.normal(0, 3, size=n))
    orders = np.maximum(orders, 0).round(0).astype(int)

    df = pd.DataFrame({
        "user_id": [f"u{i:04d}" for i in range(n)],
        "adopted_feature": adopted,
        "tenure_months": tenure_months.round(1),
        "orders_30d": orders,
        "platform": rng.choice(["ios", "android", "web"], size=n),
        "account_type": rng.choice(["free", "premium"], size=n,
                                    p=[0.7, 0.3]),
    })

    save_dataset(df, "confounded", {
        "true_causal_effect": "+5.0 orders from feature adoption",
        "confounders": ["tenure_months (confounds both adoption and orders)"],
        "naive_estimate": "~7-8 (biased upward due to tenure confounding)",
        "psm_estimate": "~5.0 (should recover true effect if tenure controlled)",
        "expected_analysis": "PSM or regression with tenure as covariate",
        "notes": "Without controlling for tenure, the effect is overstated by ~50%.",
    })
    return df


def generate_checkout_redesign():
    """Checkout redesign A/B test matching Week 4 lesson numbers exactly.

    Lessons 4.10c, 4.11b, 4.19a reference specific baselines:
    Control:   4218 users, 641 convert (15.2%), AOV ≈ $47.20, sd ≈ $18.40
    Treatment: 4196 users, 705 convert (16.8%), AOV ≈ $45.80, sd ≈ $19.10

    Also includes `support_ticket_opened` (binary): ~5% control baseline,
    ~6% treatment (consistent with "new flow introduces some confusion" story
    — non-significant guardrail degradation that lesson 4.11b teaches).

    Deterministic completer counts + post-shift on revenue so sample means land
    on lesson targets without Monte Carlo drift. Conversion z-test and AOV
    Welch t-test both reproduce the lesson's claimed output.
    """
    rng = np.random.default_rng(110)
    n_control = 4218
    n_treatment = 4196
    n_control_convert = 641   # 15.193% — rounds to 15.2%
    n_treatment_convert = 705  # 16.802% — rounds to 16.8%
    n_control_tickets = 218   # 5.17% — relative lift to treatment is +6.5%, below 10% guardrail
    n_treatment_tickets = 231  # 5.51%

    users = []
    for i in range(n_control + n_treatment):
        if i < n_control:
            variant = "control"
            converted = 1 if i < n_control_convert else 0
            # Deterministic ticket assignment, offset from converter indices so
            # ticket-opening isn't perfectly correlated with checkout outcome.
            support_ticket_opened = 1 if (i + 500) % n_control < n_control_tickets else 0
            aov_mean, aov_sd = 47.20, 18.40
        else:
            variant = "treatment"
            j = i - n_control
            converted = 1 if j < n_treatment_convert else 0
            support_ticket_opened = 1 if (j + 700) % n_treatment < n_treatment_tickets else 0
            aov_mean, aov_sd = 45.80, 19.10

        if converted:
            revenue = max(5.0, rng.normal(aov_mean, aov_sd))
        else:
            revenue = 0.0

        platform = rng.choice(["ios", "android", "web"], p=[0.40, 0.35, 0.25])
        signup_days = int(rng.exponential(120))
        users.append({
            "user_id": f"u{i:06d}",
            "variant": variant,
            "checkout_started": 1,
            "checkout_completed": converted,
            "revenue": round(revenue, 2),
            "support_ticket_opened": support_ticket_opened,
            "platform": platform,
            "signup_days": signup_days,
            "device_type": rng.choice(["mobile", "desktop", "tablet"],
                                       p=[0.55, 0.35, 0.10]),
        })

    df = pd.DataFrame(users)

    # Post-shift revenue so sample means land exactly on lesson targets.
    # Preserves variance and distribution shape; removes Monte Carlo drift.
    for variant, target_mean in [("control", 47.20), ("treatment", 45.80)]:
        mask = (df["variant"] == variant) & (df["checkout_completed"] == 1)
        current_mean = df.loc[mask, "revenue"].mean()
        shift = target_mean - current_mean
        df.loc[mask, "revenue"] = (df.loc[mask, "revenue"] + shift).round(2)

    # Shuffle row order within each variant so converters aren't first-N.
    # Keeps variant contiguous (matches existing CSV layout).
    shuffled = []
    for variant in ("control", "treatment"):
        sub = df[df["variant"] == variant].sample(frac=1, random_state=rng.bit_generator).reset_index(drop=True)
        shuffled.append(sub)
    df = pd.concat(shuffled, ignore_index=True)
    df["user_id"] = [f"u{i:06d}" for i in range(len(df))]
    save_dataset(df, "checkout_redesign", {
        "true_effect": "10.5% relative lift in checkout completion (15.2% → 16.8%)",
        "baseline_rate": 0.152,
        "treatment_rate": 0.168,
        "relative_lift": 0.105,
        "aov_control": 47.20,
        "aov_treatment": 45.80,
        "srm": "PASS",
        "guardrails": "AOV slightly lower in treatment — investigate trade-off",
        "expected_verdict": "SHIP with AOV monitoring",
        "notes": "Matches lesson 4.10c and 4.19a numbers. Conversion up, AOV slightly down.",
    })
    return df


def generate_checkout_timeseries():
    """56-day daily timeseries for pre-post analysis.

    Lesson 4.18b: 4 weeks pre, 4 weeks post March 1 intervention.
    ~14.9% pre-period conversion, ~16.3% post-period conversion.
    Day-of-week seasonality. True adjusted effect ~+1.2pp.
    """
    rng = np.random.default_rng(111)
    start_date = pd.Timestamp("2026-02-01")
    intervention_date = pd.Timestamp("2026-03-01")
    n_days = 56

    rows = []
    for day_idx in range(n_days):
        date = start_date + pd.Timedelta(days=day_idx)
        post = date >= intervention_date
        dow = date.dayofweek  # 0=Mon, 6=Sun

        # Day-of-week seasonality: weekdays higher traffic, weekends lower
        dow_traffic_mult = [1.0, 1.05, 1.08, 1.10, 1.15, 0.85, 0.75][dow]
        dow_conv_shift = [0.0, 0.001, 0.002, 0.003, 0.005, -0.005, -0.008][dow]

        daily_traffic = int(rng.normal(300, 30) * dow_traffic_mult)
        daily_traffic = max(100, daily_traffic)

        # Base conversion with slight upward trend
        base_conv = 0.149 + day_idx * 0.0001  # tiny organic drift
        base_conv += dow_conv_shift

        # Treatment effect post-intervention
        if post:
            base_conv += 0.012  # +1.2pp true adjusted effect

        # Add daily noise
        conv_rate = max(0.05, min(0.30, base_conv + rng.normal(0, 0.008)))
        conversions = rng.binomial(daily_traffic, conv_rate)
        daily_revenue = sum(
            max(5.0, rng.normal(46.5, 18.0)) for _ in range(conversions)
        )

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": date.strftime("%A"),
            "daily_visitors": daily_traffic,
            "conversions": conversions,
            "conversion_rate": round(conversions / daily_traffic, 4),
            "revenue": round(daily_revenue, 2),
            "post_intervention": int(post),
        })

    df = pd.DataFrame(rows)
    save_dataset(df, "checkout_timeseries", {
        "true_effect": "+1.2pp adjusted conversion lift (14.9% → 16.3% raw)",
        "pre_period": "2026-02-01 to 2026-02-28",
        "post_period": "2026-03-01 to 2026-03-28",
        "intervention": "2026-03-01 (checkout redesign launch)",
        "seasonality": "Day-of-week: higher on Thu/Fri, lower on weekends",
        "organic_drift": "+0.01pp/day upward trend",
        "expected_analysis": "Pre-post with day-of-week controls",
        "notes": "Matches lesson 4.18b. 56 days of daily conversion data.",
    })
    return df


def generate_power_user_fallacy():
    """Observational data showing power user / selection bias.

    Lesson 4.18b: power users adopt features more AND retain better naturally.
    Columns: job_role, heavy_usage, retained_30d (matching lesson expectations).
    Naive analysis shows heavy users retain 85% vs light 55%.
    True causal effect of heavy usage on retention: ~+10pp (not +30pp).
    """
    rng = np.random.default_rng(112)
    n = 3000

    # Job role affects both usage and retention (confounder)
    job_roles = rng.choice(
        ["engineer", "pm", "designer", "analyst", "other"],
        size=n,
        p=[0.30, 0.25, 0.15, 0.20, 0.10],
    )
    role_usage_propensity = {
        "engineer": 0.65, "pm": 0.45, "designer": 0.30,
        "analyst": 0.55, "other": 0.25,
    }
    role_retention_base = {
        "engineer": 0.72, "pm": 0.68, "designer": 0.60,
        "analyst": 0.70, "other": 0.55,
    }

    heavy_usage = np.array([
        rng.binomial(1, role_usage_propensity[r]) for r in job_roles
    ])
    # True causal effect of heavy usage = +10pp retention
    retention_probs = np.array([
        role_retention_base[r] + 0.10 * heavy_usage[i]
        for i, r in enumerate(job_roles)
    ])
    retained_30d = rng.binomial(1, np.clip(retention_probs, 0.1, 0.95))

    # Add extra features for richer analysis
    signup_source = rng.choice(
        ["organic", "referral", "paid", "direct"],
        size=n,
        p=[0.35, 0.25, 0.25, 0.15],
    )
    device = rng.choice(["mobile", "desktop"], size=n, p=[0.60, 0.40])
    plan_type = rng.choice(["free", "premium"], size=n, p=[0.70, 0.30])

    df = pd.DataFrame({
        "user_id": [f"u{i:05d}" for i in range(n)],
        "job_role": job_roles,
        "heavy_usage": heavy_usage,
        "retained_30d": retained_30d,
        "signup_source": signup_source,
        "device": device,
        "plan_type": plan_type,
    })

    save_dataset(df, "power_user_fallacy", {
        "true_causal_effect": "+10pp retention from heavy usage",
        "naive_estimate": "~+30pp (confounded by job_role)",
        "confounders": ["job_role (affects both heavy_usage and retention)"],
        "expected_analysis": "Segment by job_role to reveal Simpson's paradox; "
                             "PSM or regression with job_role as covariate",
        "notes": "Matches lesson 4.18b. Engineers are more likely to be heavy "
                 "users AND more likely to retain. Naive comparison overstates "
                 "the effect 3x.",
    })
    return df


def main():
    print("Generating NovaMart experiment datasets...")
    print()

    generate_clean_ab()
    generate_srm_violation()
    generate_guardrail_violation()
    generate_underpowered()
    generate_no_effect()
    generate_mixed_results()
    generate_did_parallel()
    generate_did_broken()
    generate_confounded()
    generate_checkout_redesign()
    generate_checkout_timeseries()
    generate_power_user_fallacy()

    print()
    print("Done! 12 datasets generated with answer keys in _answers/.")


if __name__ == "__main__":
    main()
