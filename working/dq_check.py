"""Data Quality Check on support_tickets table."""
import duckdb

con = duckdb.connect("data/practice/novamart_practice.duckdb", read_only=True)

print("=" * 60)
print("DATA QUALITY CHECK: support_tickets")
print("=" * 60)

print("\n[1] Schema")
schema = con.execute("DESCRIBE support_tickets").fetchall()
for col, dtype, *_ in schema:
    print(f"  {col:20s} {dtype}")

print("\n[2] Row count and PK uniqueness")
n = con.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]
n_unique = con.execute("SELECT COUNT(DISTINCT ticket_id) FROM support_tickets").fetchone()[0]
print(f"  rows: {n:,}")
print(f"  unique ticket_id: {n_unique:,}  (PK ok? {n == n_unique})")

print("\n[3] Date range")
rng = con.execute("""
  SELECT MIN(created_date) AS min_d, MAX(created_date) AS max_d,
         COUNT(DISTINCT created_date) AS n_days
  FROM support_tickets
""").fetchone()
print(f"  min: {rng[0]}   max: {rng[1]}   distinct days: {rng[2]}")

print("\n[4] Null rates per column")
cols = [c[0] for c in schema]
for col in cols:
    null_pct = con.execute(
        f"SELECT 100.0*SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END)/COUNT(*) FROM support_tickets"
    ).fetchone()[0]
    flag = " <-- HIGH" if null_pct > 5 else ""
    print(f"  {col:20s} {null_pct:6.2f}%{flag}")

print("\n[5] Category distribution")
for row in con.execute("""
  SELECT category, COUNT(*) AS n, ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (), 1) AS pct
  FROM support_tickets GROUP BY 1 ORDER BY 2 DESC
""").fetchall():
    print(f"  {row[0]:18s} {row[1]:6,d}  {row[2]:5.1f}%")

print("\n[6] Severity distribution")
for row in con.execute("""
  SELECT severity, COUNT(*) AS n, ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (), 1) AS pct
  FROM support_tickets GROUP BY 1 ORDER BY 2 DESC
""").fetchall():
    print(f"  {row[0]:18s} {row[1]:6,d}  {row[2]:5.1f}%")

print("\n[7] Status distribution")
for row in con.execute("""
  SELECT status, COUNT(*) AS n FROM support_tickets GROUP BY 1
""").fetchall():
    print(f"  {row[0]:18s} {row[1]:6,d}")

print("\n[8] Device distribution")
for row in con.execute("""
  SELECT device, COUNT(*) AS n FROM support_tickets GROUP BY 1 ORDER BY 2 DESC
""").fetchall():
    print(f"  {str(row[0]):18s} {row[1]:6,d}")

print("\n[9] App version distribution")
for row in con.execute("""
  SELECT app_version, COUNT(*) AS n FROM support_tickets GROUP BY 1 ORDER BY 2 DESC
""").fetchall():
    print(f"  {str(row[0]):18s} {row[1]:6,d}")
