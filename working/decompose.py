"""Decompose the spike: category, device, app_version, country, channel.
Compare spike window (Jun 1-14, 2024) vs prior 28-day baseline (May 4-31, 2024).
"""
import duckdb

con = duckdb.connect("data/practice/novamart_practice.duckdb", read_only=True)

SPIKE_START = "2024-06-01"
SPIKE_END   = "2024-06-14"
BASE_START  = "2024-05-04"
BASE_END    = "2024-05-31"

def lift_table(group_col, label, joined=False, where=""):
    """Print a daily-rate-lift table for a grouping column."""
    extra_join = (
        " JOIN users u ON u.user_id = t.user_id "
        if joined else ""
    )
    sql = f"""
    WITH spike AS (
      SELECT {group_col} AS grp, COUNT(*)/14.0 AS daily_rate, COUNT(*) AS n
      FROM support_tickets t {extra_join}
      WHERE created_date BETWEEN '{SPIKE_START}' AND '{SPIKE_END}' {where}
      GROUP BY 1
    ),
    base AS (
      SELECT {group_col} AS grp, COUNT(*)/28.0 AS daily_rate, COUNT(*) AS n
      FROM support_tickets t {extra_join}
      WHERE created_date BETWEEN '{BASE_START}' AND '{BASE_END}' {where}
      GROUP BY 1
    )
    SELECT COALESCE(s.grp, b.grp) AS grp,
           COALESCE(b.daily_rate, 0) AS base_per_day,
           COALESCE(s.daily_rate, 0) AS spike_per_day,
           COALESCE(s.daily_rate,0) - COALESCE(b.daily_rate,0) AS abs_lift_per_day,
           CASE WHEN COALESCE(b.daily_rate,0) > 0
                THEN 100.0*(COALESCE(s.daily_rate,0)/b.daily_rate - 1)
                ELSE NULL END AS pct_lift,
           COALESCE(s.n,0) AS spike_n,
           COALESCE(b.n,0) AS base_n
    FROM spike s FULL OUTER JOIN base b ON s.grp = b.grp
    ORDER BY abs_lift_per_day DESC
    """
    rows = con.execute(sql).fetchall()
    print(f"\n[{label}] daily rate lift, spike vs prior 28d baseline")
    print(f"  {'group':22s} {'base/d':>8s} {'spike/d':>8s} {'lift/d':>8s} {'%lift':>7s} {'spike_n':>8s} {'base_n':>8s}")
    for r in rows:
        grp, b, s, lift, pct, sn, bn = r
        pct_str = f"{pct:6.0f}%" if pct is not None else "    --"
        print(f"  {str(grp):22s} {b:8.2f} {s:8.2f} {lift:+8.2f} {pct_str} {sn:8d} {bn:8d}")

# Total volume
print("=" * 70)
print(f"TOTAL volume: spike window ({SPIKE_START}..{SPIKE_END}, 14d) vs baseline ({BASE_START}..{BASE_END}, 28d)")
print("=" * 70)
totals = con.execute(f"""
  SELECT
    SUM(CASE WHEN created_date BETWEEN '{SPIKE_START}' AND '{SPIKE_END}' THEN 1 ELSE 0 END) AS spike_n,
    SUM(CASE WHEN created_date BETWEEN '{BASE_START}'  AND '{BASE_END}'  THEN 1 ELSE 0 END) AS base_n
  FROM support_tickets
""").fetchone()
print(f"  spike total: {totals[0]:,}  ({totals[0]/14:.1f}/day)")
print(f"  base total:  {totals[1]:,}  ({totals[1]/28:.1f}/day)")
print(f"  daily-rate lift: {totals[0]/14 - totals[1]/28:+.1f}/day  ({100*(totals[0]/14)/(totals[1]/28)-100:+.0f}%)")

lift_table("category", "Category")
lift_table("device", "Device")
lift_table("COALESCE(app_version, '(web/none)')", "App version")
lift_table("severity", "Severity")
lift_table("u.country", "User country", joined=True)
lift_table("u.acquisition_channel", "User acquisition channel", joined=True)

# Combined: device x category
print("\n[Device x Category] spike lift per day, payment_issue focus")
combo = con.execute(f"""
  WITH spike AS (
    SELECT device, category, COUNT(*)/14.0 AS r FROM support_tickets
    WHERE created_date BETWEEN '{SPIKE_START}' AND '{SPIKE_END}' GROUP BY 1,2
  ),
  base AS (
    SELECT device, category, COUNT(*)/28.0 AS r FROM support_tickets
    WHERE created_date BETWEEN '{BASE_START}' AND '{BASE_END}' GROUP BY 1,2
  )
  SELECT COALESCE(s.device,b.device) d, COALESCE(s.category,b.category) c,
         COALESCE(b.r,0) AS base_r, COALESCE(s.r,0) AS spike_r,
         COALESCE(s.r,0)-COALESCE(b.r,0) AS lift
  FROM spike s FULL OUTER JOIN base b USING (device, category)
  ORDER BY lift DESC LIMIT 12
""").fetchall()
print(f"  {'device':10s} {'category':18s} {'base/d':>8s} {'spike/d':>8s} {'lift/d':>8s}")
for d, c, br, sr, lift in combo:
    print(f"  {str(d):10s} {str(c):18s} {br:8.2f} {sr:8.2f} {lift:+8.2f}")

# iOS app_version drilldown for payment_issue
print("\n[iOS payment_issue by app_version, spike window]")
for row in con.execute(f"""
  SELECT app_version, COUNT(*) AS n
  FROM support_tickets
  WHERE created_date BETWEEN '{SPIKE_START}' AND '{SPIKE_END}'
    AND device='ios' AND category='payment_issue'
  GROUP BY 1 ORDER BY 2 DESC
""").fetchall():
    print(f"  {str(row[0]):10s} {row[1]:,}")

print("\n[iOS payment_issue by app_version, baseline window]")
for row in con.execute(f"""
  SELECT app_version, COUNT(*) AS n
  FROM support_tickets
  WHERE created_date BETWEEN '{BASE_START}' AND '{BASE_END}'
    AND device='ios' AND category='payment_issue'
  GROUP BY 1 ORDER BY 2 DESC
""").fetchall():
    print(f"  {str(row[0]):10s} {row[1]:,}")
