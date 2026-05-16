# VR20 Strategy — Design Spec
**Date:** 2026-05-16  
**Status:** Approved — ready for implementation  
**Backtest result:** ₹+73,943 over 6 months (Dec 2025–May 2026), NIFTY only  
**vs VR10:** +23% total P&L, significantly better in choppy/reversing months

---

## 1. Context

VR10 is a PE-only options bot that earns well in sustained downtrends but struggles in transitional markets (Dec 2025: ₹-21k, Apr 2026: underperforms). VR20 is a clean rebuild around 10 trading principles — bidirectional (PE + CE), principle-driven entry, adaptive risk management. VR10 is kept running unchanged. Both run in parallel for 4–6 weeks; the better performer goes to full capital.

---

## 2. File Structure

```
~/groww-bot/
  vr20_bot.py              ← new strategy (this spec)
  vr20_config.json         ← runtime config (target/stop/regime/boosters)
  vr20_journal.py          ← Google Sheets logger (called on trade close)
  agent_decisions_vr20.json← strategy agent output for VR20
  multi_runner.py          ← updated: orchestrates VR10 + VR20 side by side
```

VR20 does NOT modify `vr10_bot.py`, `vr10_config.json`, or any existing VR10 files.

---

## 3. Signal Engine

### 3.1 Evaluation Time
Signal fires at **candle 30 (9:44 AM)** — same as VR10. Entry is at the close price of candle 30.

### 3.2 Three-Timeframe Trend Check (Principle 3)
All three timeframes must agree for a trade to fire.

| Timeframe | Computation | Bear condition | Bull condition |
|-----------|-------------|---------------|---------------|
| Weekly | 25-day EMA of previous daily closes | prev_close < 25d_EMA | prev_close > 25d_EMA |
| Daily | 20-day EMA of previous daily closes | today_open < 20d_EMA | today_open > 20d_EMA |
| Intraday | EMA9 vs EMA21 on first 30 candles | EMA9 < EMA21 | EMA9 > EMA21 |

- All three bear → PE candidate  
- All three bull → CE candidate  
- Any conflict → **SKIP** (no trade)

EMA data is computed from `nifty_data_cache.json` daily close series, updated by `update_cache.py`.

### 3.3 VWAP Direction Confirmation
- PE requires: `close30 < VWAP30` (intraday close below VWAP at 9:44)
- CE requires: `close30 > VWAP30`

If trend and VWAP conflict → SKIP.

### 3.4 Conviction Score (Principle 6 + 9)

```
Component                          PE pts   CE pts
─────────────────────────────────────────────────
Weekly trend aligned                  20       20
Daily trend aligned                   20       20
Intraday EMA aligned (mandatory)      20       20
2+ HQ boosters firing                 20       20
1 HQ booster firing                   10       10
OR range 80–150 (tradeable)           10       10
VWAP distance ≥ 0.15%                 10       10
─────────────────────────────────────────────────
Maximum                              100      100
```

**PE HQ boosters** (win rate ≥ 0.70 in VR10 config): `orb_up`, `gap_bull`, `is_friday`, `is_expiry`, `ema_bear`  
**CE HQ boosters** (assumed): `gap_bull`, `is_friday`, `orb_up`, `prev_bull`

Lot sizing by score:

| Score | Lots |
|-------|------|
| 80–100 | 3 |
| 60–79 | 2 |
| 40–59 | 1 |
| < 40 | SKIP |

### 3.5 Intraday EMA — Mandatory Gate
`ema_bear` (EMA9 < EMA21) is mandatory for PE. `ema_bull` mandatory for CE. If the mandatory gate fails → SKIP regardless of other signals.

---

## 4. Trade Management

### 4.1 Dynamic Target — Principle 2 (Volatility Calibration)

| OR Range | Target (premium %) | Reasoning |
|----------|--------------------|-----------|
| < 80 pts | 35% | Low-energy day — realistic target |
| 80–129 pts | 55% | Normal range — VR10 baseline |
| 130–199 pts | 75% | High energy — bigger move likely |
| ≥ 200 pts | SKIP | Too volatile — unpredictable |

### 4.2 Adaptive Stop — Principle 5 (Invalidation-based)

Stop is placed at the point where the trade thesis is provably wrong:
- **PE stop:** OR High (if price closes above OR High, bearish thesis is invalid)
- **CE stop:** OR Low (if price closes below OR Low, bullish thesis is invalid)

Conversion to premium %:
```python
dist = OR_HIGH - entry_spot          # PE: how far spot must rise to hit stop
stop_pct = (dist * delta) / entry_prem
stop_pct = min(stop_pct, 0.50)       # hard cap: never risk > 50% of premium
```

If `entry_spot >= OR_HIGH` (PE) or `entry_spot <= OR_LOW` (CE) at signal time → stop already triggered → SKIP.

### 4.3 R:R Gate — Principle 1 (Non-negotiable)
```
R:R = target_pct / stop_pct
If R:R < 1.5 → SKIP (log reason)
```
This gate fires after computing dynamic target and adaptive stop. A trade with bad R:R geometry is rejected even if all signals fire.

### 4.4 Breakeven Trail — Principle 8
Once premium reaches **+25% of entry premium**, stop is moved to entry (breakeven). From that point, worst case is scratch — the trade is free.

```python
if current_prem >= entry_prem * 1.25:
    stop = entry_prem  # move to breakeven
```

### 4.5 Time Stop — Principle 7
- **11:30 AM (candle 135):** If trade is not yet profitable (premium < entry), tighten stop to breakeven. Force a scratch rather than holding a loser.
- **12:30 PM (candle 195):** Hard exit unconditionally. No exceptions.

### 4.6 Exit Priority (candle-level)
1. Target hit → TARGET exit, log premium gain
2. Stop hit → STOP or BREAKEVEN exit
3. 11:30 tighten (if underwater)
4. 12:30 hard exit → TIME exit

---

## 5. Mon/Tue Handling

VR10 blocks Mon/Tue unless 2+ HQ boosters fire. VR20 does not block Mon/Tue but conviction scoring naturally reduces lot size on weaker Mon/Tue setups. A Mon/Tue day with no HQ boosters will score ≤ 60 → 1-2 lots max.

---

## 6. CE Side

CE is fully enabled in VR20. Same lot sizing, same R:R gate, same time management as PE. Direction is determined by three-timeframe alignment (all bull → CE). CE stop is placed at OR Low. CE target is same dynamic scale by OR range.

CE is **not active** in VR10 config. The two strategies are independent.

---

## 7. Google Sheets Journal

### 7.1 Architecture
`vr20_journal.py` uses `gspread` library with a Google service account. One sheet per index. Rows appended after every trade close event.

### 7.2 Sheet Schema

| Col | Field | Source |
|-----|-------|--------|
| A | Date | system |
| B | Day | system |
| C | Direction | signal |
| D | Entry Time | system |
| E | Entry Spot | signal |
| F | OR High | features |
| G | OR Low | features |
| H | OR Range | features |
| I | Stop Level (spot) | computed |
| J | Target Level (spot) | computed |
| K | R:R Ratio | computed (Principle 1) |
| L | OR Range Bucket | S/M/L (Principle 2) |
| M | Weekly Trend | BULL/BEAR (Principle 3) |
| N | Daily Trend | BULL/BEAR (Principle 3) |
| O | Intraday EMA | bear/bull (Principle 3) |
| P | Entry Quality | VWAP dist % (Principle 4) |
| Q | Stop Logic | OR_HIGH/OR_LOW/capped (Principle 5) |
| R | Lots | 1/2/3 (Principle 6) |
| S | Time Stop Used? | Y/N (Principle 7) |
| T | BE Trail Fired? | Y/N + time (Principle 8) |
| U | Conviction Score | 0–100 (Principle 9) |
| V | Boosters Hit | comma-separated |
| W | Exit Time | system |
| X | Exit Spot | system |
| Y | Outcome | TARGET/STOP/TIME/BREAKEVEN |
| Z | Premium Pts | gain/loss in pts |
| AA | P&L (₹) | computed |
| AB | Cumulative P&L | running total |
| AC | What Worked | **manual — user fills** |
| AD | What Didn't | **manual — user fills** |
| AE | Action Next Trade | **manual — user fills** |

### 7.3 Second Sheet — Weekly Summary (auto-computed formulas)
- Win rate, stop rate, avg R:R achieved vs planned
- Best booster combination, worst day-of-week
- P&L curve (running cumulative)
- Month-by-month breakdown

---

## 8. Config File — vr20_config.json

```json
{
  "stop_pct_cap": 0.50,
  "target_or_buckets": {"lt80": 0.35, "lt130": 0.55, "lt200": 0.75},
  "min_rr": 1.5,
  "be_trigger": 1.25,
  "conviction_lots": {"80": 3, "60": 2, "40": 1},
  "pe_active": true,
  "ce_active": true,
  "hi_q_min_wr": 0.70,
  "pe_hq_boosters": ["orb_up", "gap_bull", "is_friday", "is_expiry"],
  "ce_hq_boosters": ["gap_bull", "is_friday", "orb_up", "prev_bull"],
  "regime_score": 0.0,
  "regime_bias": "NEUTRAL"
}
```

---

## 9. multi_runner.py Changes

- Run `vr20_bot.py` alongside `vr10_bot.py` for each user account
- EOD Telegram message includes both strategies side by side:
  ```
  📊 EOD | NIFTY | 16-May
  VR10: PE — TIME exit — +₹2,317
  VR20: CE — TARGET hit — +₹13,311
  ```
- Journal write called from VR20 on trade close (not from multi_runner)

---

## 10. Validation Criteria (go-live decision)

After 4–6 weeks of parallel running:

| Metric | Go-live threshold |
|--------|------------------|
| VR20 trades | ≥ 20 |
| VR20 win rate | ≥ VR10 win rate |
| VR20 total P&L | ≥ VR10 total P&L |
| VR20 worst month | ≥ VR10 worst month |
| VR20 stop rate | ≤ 35% |

If VR20 passes all 5 → replace VR10 as primary. If VR20 fails ≥ 2 → keep VR10, debug VR20.

---

## 11. Out of Scope

- BANKNIFTY and FINNIFTY (added after NIFTY validation)
- ML-based regime prediction
- Live option chain scanning (premium still estimated via delta)
- Trailing stop beyond breakeven (future enhancement)
