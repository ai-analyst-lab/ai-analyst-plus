"""Detect ticket spike: daily trend with rolling baseline + z-score anomaly detection."""
import duckdb
import pandas as pd

con = duckdb.connect("data/practice/novamart_practice.duckdb", read_only=True)

# Daily ticket counts
daily = con.execute("""
  SELECT created_date, COUNT(*) AS tickets
  FROM support_tickets
  GROUP BY 1 ORDER BY 1
""").fetch_df()
daily["created_date"] = pd.to_datetime(daily["created_date"])
print(f"Days: {len(daily)}, total tickets: {daily['tickets'].sum():,}")
print(f"Median daily tickets: {daily['tickets'].median():.0f}")
print(f"Mean daily tickets:   {daily['tickets'].mean():.1f}")
print(f"Std daily tickets:    {daily['tickets'].std():.1f}")

# 28-day trailing baseline (excluding the current day)
daily["baseline_mean"] = daily["tickets"].shift(1).rolling(28, min_periods=14).mean()
daily["baseline_std"]  = daily["tickets"].shift(1).rolling(28, min_periods=14).std()
daily["zscore"] = (daily["tickets"] - daily["baseline_mean"]) / daily["baseline_std"]
daily["pct_above_baseline"] = (daily["tickets"] / daily["baseline_mean"] - 1) * 100

# Top anomalies by z-score
print("\nTop 15 days by z-score above 28-day rolling baseline:")
top = daily.dropna().nlargest(15, "zscore")[
    ["created_date", "tickets", "baseline_mean", "zscore", "pct_above_baseline"]
]
print(top.to_string(index=False))

# Find longest contiguous run of z>2 days (the "spike window")
above = daily["zscore"] > 2
runs = []
start = None
for i, hit in enumerate(above):
    if hit and start is None:
        start = i
    elif not hit and start is not None:
        runs.append((start, i - 1))
        start = None
if start is not None:
    runs.append((start, len(above) - 1))

print("\nContiguous runs where daily tickets > baseline + 2 std:")
for s, e in runs:
    sd = daily.iloc[s]["created_date"].date()
    ed = daily.iloc[e]["created_date"].date()
    n = e - s + 1
    excess = int((daily.iloc[s:e+1]["tickets"] - daily.iloc[s:e+1]["baseline_mean"]).sum())
    print(f"  {sd} -> {ed} ({n} days), excess tickets vs baseline: {excess:+,}")

# Save for chart and downstream steps
daily.to_csv("working/daily_tickets.csv", index=False)
print("\nSaved working/daily_tickets.csv")
