---
name: forecast
description: Generate time-series forecasts and projections for metrics. Use when users ask what will happen next, forecast/project/predict a metric, extrapolate trends, or plan capacity/budget from historical data.
---

# Forecast

## Purpose
Create decision-oriented time-series forecasts with baselines, assumptions, confidence ranges, and caveats.

## Workflow
1. Clarify the decision, forecast horizon, audience, and known upcoming changes when not obvious.
2. Identify the metric source from `.knowledge/datasets/{active}/metrics/`, schema docs, or the user's explicit data.
3. Query or load data aggregated to an appropriate daily/weekly/monthly grain.
4. Validate sufficiency: at least 14 points for short-term forecasts, 30+ for seasonality, and 60+ for quarterly/longer projections.
5. Build a pandas Series with `DatetimeIndex`; clean gaps transparently.
6. Run at least two methods from `helpers.forecast_helpers.py` when available: naive baseline, seasonal naive if seasonality exists, exponential smoothing, and Holt-Winters when warranted.
7. Compare against a naive baseline and select the simplest method that performs adequately.
8. Create a chart with historical line, forecast line, confidence band, and forecast boundary using chart helpers.
9. Translate results to the decision: capacity, budget, monitoring threshold, or executive implication.

## Output contract
- State history length, horizon, method, baseline comparison, seasonality, key forecast milestones, confidence range, and assumptions.
- Include chart path when generated.
- If data is insufficient or structurally broken, say forecasts are unreliable and explain what data is needed.

## Safety
- Forecasts assume past patterns continue unless scenarios are modeled.
- Never present point forecasts without uncertainty and caveats.
