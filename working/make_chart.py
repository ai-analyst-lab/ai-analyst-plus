"""SWD-styled trend chart: daily support tickets, with iOS payment_issue
highlighted and the Jun 1-14 spike window shaded.
"""
import sys
sys.path.insert(0, ".")

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from helpers.chart_helpers import (
    swd_style, COLORS, action_title, format_date_axis,
    save_chart, add_event_span, CHART_FIGSIZE,
)

con = duckdb.connect("data/practice/novamart_practice.duckdb", read_only=True)

# Daily series: total tickets, iOS payment_issue, all other
daily = con.execute("""
  SELECT
    created_date,
    COUNT(*)                                                            AS total,
    SUM(CASE WHEN device='ios' AND category='payment_issue' THEN 1 ELSE 0 END) AS ios_payment,
    SUM(CASE WHEN NOT (device='ios' AND category='payment_issue') THEN 1 ELSE 0 END) AS other
  FROM support_tickets
  GROUP BY 1 ORDER BY 1
""").fetch_df()
daily["created_date"] = pd.to_datetime(daily["created_date"])

# 7-day rolling smooth so the lines read as trends, not noise
for col in ["total", "ios_payment", "other"]:
    daily[f"{col}_7d"] = daily[col].rolling(7, min_periods=1).mean()

colors = swd_style()
fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

x = daily["created_date"]

# Background: all OTHER tickets (gray)
ax.plot(x, daily["other_7d"], color=COLORS["gray400"], linewidth=1.5,
        label="All other tickets", zorder=1)

# Foreground: iOS payment_issue (action amber)
ax.plot(x, daily["ios_payment_7d"], color=COLORS["action"], linewidth=2.8,
        label="iOS payment_issue", zorder=3)

# Shade Jun 1-14 spike window
add_event_span(ax,
               pd.Timestamp("2024-06-01"),
               pd.Timestamp("2024-06-14"),
               label="Jun 1-14 spike",
               color=COLORS["accent"],
               alpha=0.10)

# Annotate iOS 2.3.0 release
peak_date = pd.Timestamp("2024-06-04")
peak_y    = daily.loc[daily["created_date"] == peak_date, "ios_payment_7d"].values
if len(peak_y):
    ax.annotate(
        "iOS v2.3.0 released Jun 1\npayment bug -> +681% iOS payment tickets",
        xy=(peak_date, peak_y[0]),
        xytext=(pd.Timestamp("2024-07-15"), peak_y[0] + 8),
        fontsize=9, color=COLORS["gray900"],
        arrowprops=dict(arrowstyle="->", color=COLORS["gray600"], lw=0.8),
    )

ax.set_ylabel("Tickets per day (7-day rolling avg)", fontsize=10, color=COLORS["gray600"])
ax.set_xlabel("")
ax.set_ylim(0, max(80, daily["total_7d"].max() * 1.15))
format_date_axis(ax, fmt="%b")

# End-of-line labels
last = daily.iloc[-1]
ax.text(last["created_date"] + pd.Timedelta(days=2), last["other_7d"], "Other",
        va="center", fontsize=9, color=COLORS["gray400"])
ax.text(last["created_date"] + pd.Timedelta(days=2), last["ios_payment_7d"], "iOS payment",
        va="center", fontsize=9, fontweight="bold", color=COLORS["action"])

action_title(
    ax,
    "iOS v2.3.0 payment bug drove the June ticket spike",
    "Daily support tickets, 2024  |  Source: support_tickets table"
)

save_chart(fig, "outputs/charts/ticket_spike_trend.png")
print("Saved outputs/charts/ticket_spike_trend.png")
