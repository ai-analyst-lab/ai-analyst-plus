"""
vr20_bot.py  —  VR20 Principle-First Strategy

Runs independently of vr10_bot.py. Same Groww API, same VM.
DO NOT edit vr10_bot.py — this is a clean parallel strategy.

Core principles implemented:
  1. R:R >= 1.5 enforced pre-entry (hard gate)
  2. Dynamic target calibrated to OR range size
  3. Three-timeframe trend alignment (weekly / daily / intraday)
  4. Entry only at decision points (VWAP + OR boundaries)
  5. Adaptive stop placed at trade invalidation (OR High/Low)
  6. Conviction score (0-100) drives lot sizing
  7. Time stop: tighten at 11:30, hard exit 12:30
  8. Breakeven trail fires at +25% premium gain
  9. CE and PE are equal citizens (bidirectional)
 10. Every trade logged to Google Sheets journal
"""

import os, json, asyncio, time, warnings
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")

# ── Env ───────────────────────────────────────────────────────────────────────
_ENV = Path(__file__).parent / ".env"
if _ENV.exists():
    for _l in _ENV.read_text(encoding="utf-8").splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            _k, _, _v = _l.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from growwapi import GrowwAPI

IST = ZoneInfo("Asia/Kolkata")

def _reload_env():
    if _ENV.exists():
        for _l in _ENV.read_text(encoding="utf-8").splitlines():
            _l = _l.strip()
            if _l and not _l.startswith("#") and "=" in _l:
                _k, _, _v = _l.partition("=")
                os.environ[_k.strip()] = _v.strip()

def _client() -> GrowwAPI:
    _reload_env()
    return GrowwAPI(os.environ["GROWW_ACCESS_TOKEN"])

TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

# ── Per-index config ──────────────────────────────────────────────────────────
import argparse as _ap
_p = _ap.ArgumentParser(add_help=False)
_p.add_argument("--index", default="NIFTY")
_ARGS, _ = _p.parse_known_args()

_IDX_MAP = {
    "NIFTY":     {"symbol":"NIFTY",     "lot":65,  "expiry_dow":1, "atm_step":50,  "cache":"nifty_data_cache.json"},
    "BANKNIFTY": {"symbol":"BANKNIFTY", "lot":15,  "expiry_dow":1, "atm_step":100, "cache":"banknifty_data_cache.json"},
    "FINNIFTY":  {"symbol":"FINNIFTY",  "lot":40,  "expiry_dow":1, "atm_step":50,  "cache":"finnifty_data_cache.json"},
}
_IDX       = _IDX_MAP.get(_ARGS.index.upper(), _IDX_MAP["NIFTY"])
INDEX_NAME = _IDX["symbol"]
EXPIRY_DOW = _IDX["expiry_dow"]
ATM_STEP   = _IDX["atm_step"]
LOT_SIZE   = _IDX["lot"]
CACHE_F    = Path(__file__).parent / _IDX["cache"]
CONFIG_F   = Path(__file__).parent / f"vr20_config_{INDEX_NAME.lower()}.json"
LOG_F      = Path(__file__).parent / f"vr20_{INDEX_NAME.lower()}.log"

CAPITAL    = int(os.environ.get("CAPITAL", "30000"))
PAPER_MODE = os.environ.get("PAPER_MODE", "0") == "1"
DEPLOY     = 0.40
DELTA      = 0.45   # PE/CE delta — calibrated from backtest

# ── VR20 fixed parameters ─────────────────────────────────────────────────────
B30          = 30    # signal candle index (9:44 AM)
OR_END       = 15    # OR window: first 15 candles (9:15–9:29)
MIN_RR       = 1.5   # minimum R:R — hard gate
BE_TRIGGER   = 1.25  # breakeven trail fires when prem reaches 125% of entry
TIME_TIGHTEN = (11, 30)   # tighten stop to BE if not profitable at 11:30
TIME_EXIT    = (12, 30)   # unconditional exit

# ── Logging & Telegram ────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now(IST).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_F, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def tg(msg: str):
    if not TG_TOKEN or not TG_CHAT:
        return
    import urllib.request
    try:
        data = json.dumps({"chat_id": TG_CHAT,
                           "text": f"[VR20-{INDEX_NAME}] {msg}"}).encode()
        req  = urllib.request.Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass

# ── Config ────────────────────────────────────────────────────────────────────
_DEFAULT_CFG = {
    "target_or_buckets": {"lt80": 0.35, "lt130": 0.55, "lt200": 0.75},
    "stop_pct_cap": 0.50,
    "min_rr": 1.5,
    "be_trigger": 1.25,
    "conviction_lots": {"80": 3, "60": 2, "40": 1},
    "pe_active": True, "ce_active": True,
    "hi_q_min_wr": 0.70,
    "pe_hq_boosters": ["orb_up", "gap_bull", "is_friday", "is_expiry"],
    "ce_hq_boosters": ["gap_bull", "is_friday", "orb_up", "prev_bull"],
    "regime_score": 0.0, "regime_bias": "NEUTRAL",
    "blocked_days": [],
}

def load_config() -> dict:
    if CONFIG_F.exists():
        try:
            return {**_DEFAULT_CFG, **json.loads(CONFIG_F.read_text())}
        except Exception:
            pass
    return _DEFAULT_CFG.copy()

# ── Shared math helpers ───────────────────────────────────────────────────────
def _ema(arr, p):
    if len(arr) < p:
        return float(arr[-1]) if arr else 0.0
    m = 2 / (p + 1); e = float(np.mean(arr[:p]))
    for v in arr[p:]:
        e = float(v) * m + e * (1 - m)
    return e

def _vwap(c, v):
    s = float(np.sum(v))
    return float(np.dot(c, v) / s) if s else float(np.mean(c))

def _rsi(prices, period=9):
    if len(prices) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(prices)):
        d = float(prices[i]) - float(prices[i - 1])
        gains.append(max(d, 0)); losses.append(max(-d, 0))
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

# ── Feature computation (intraday, same logic as VR10) ────────────────────────
def compute_features(data: dict, prev: dict | None, day_date: date) -> dict:
    o = np.array(data["o"]); h = np.array(data["h"])
    l = np.array(data["l"]); c = np.array(data["c"])
    v = np.array(data["v"]); n = len(c)

    or_end = min(OR_END, n)
    OR_H   = float(np.max(h[:or_end]))
    OR_L   = float(np.min(l[:or_end]))
    OR_rng = OR_H - OR_L

    b30    = min(B30, n - 1)
    vwap30 = _vwap(c[:b30 + 1], v[:b30 + 1])
    below_v = float(c[b30]) < vwap30
    e9     = _ema(list(c[:b30 + 1]), 9)
    e21    = _ema(list(c[:b30 + 1]), 21)
    ema_bear = e9 < e21

    gap = float(o[0]) - float(prev["c"][-1]) if prev else 0.0
    f15_bear = float(c[min(14, n - 1)]) < float(o[0])

    or_break = None
    for i in range(or_end, b30 + 1):
        if h[i] > OR_H: or_break = "UP"; break
        if l[i] < OR_L: or_break = "DN"; break

    prev_bull = (float(prev["c"][-1]) > float(prev["o"][0])) if prev else None
    rsi9 = _rsi(list(c[:b30 + 1]))
    vwap_dist_pct = round((float(c[b30]) - vwap30) / vwap30 * 100, 3) if vwap30 > 0 else 0.0

    dow = day_date.weekday()
    return {
        "below_vwap30": bool(below_v),
        "above_vwap30": not bool(below_v),
        "vwap30":       round(vwap30, 2),
        "close30":      round(float(c[b30]), 2),
        "open_price":   round(float(o[0]), 2),
        "OR_H": round(OR_H, 1), "OR_L": round(OR_L, 1), "OR_rng": round(OR_rng, 1),
        "gap":          round(gap, 1),
        "orb_up":       or_break == "UP",
        "orb_dn":       or_break == "DN",
        "gap_bull":     gap > 25,
        "gap_bear":     gap < -5,
        "is_friday":    dow == 4,
        "is_expiry":    dow == EXPIRY_DOW,
        "ema_bear":     bool(ema_bear),
        "ema_bull":     not bool(ema_bear),
        "prev_bear":    prev_bull is False,
        "prev_bull":    prev_bull is True,
        "f15_bear":     bool(f15_bear),
        "f15_bull":     not bool(f15_bear),
        "or_normal":    80 <= OR_rng < 130,
        "rsi9":         round(rsi9, 1),
        "vwap_dist_pct": vwap_dist_pct,
        "dow":          dow,
    }

# ── Weekly / daily trend from cache ──────────────────────────────────────────
def compute_trend(cache: dict, today_str: str, today_open: float) -> dict:
    """
    weekly_bear: yesterday's close < 25-day EMA of daily closes
    daily_bear:  today's open < 20-day EMA of daily closes
    """
    sorted_days = sorted(k for k in cache if k < today_str)

    # Daily closes from cache
    closes = [float(cache[d]["c"][-1]) for d in sorted_days]

    if len(closes) >= 5:
        w_ema = _ema(closes, min(25, len(closes)))
        weekly_bear = closes[-1] < w_ema
    else:
        weekly_bear = None  # not enough data

    if len(closes) >= 5:
        d_ema = _ema(closes, min(20, len(closes)))
        daily_bear = today_open < d_ema
    else:
        daily_bear = None

    return {
        "weekly_bear": weekly_bear,
        "daily_bear":  daily_bear,
        "w_ema": round(w_ema, 1) if len(closes) >= 5 else None,
        "d_ema": round(d_ema, 1) if len(closes) >= 5 else None,
        "prev_close": closes[-1] if closes else None,
    }

# ── VR20 signal evaluation ─────────────────────────────────────────────────────
def evaluate_signal(feat: dict, trend: dict) -> dict | None:
    cfg          = load_config()
    pe_active    = cfg.get("pe_active", True)
    ce_active    = cfg.get("ce_active", True)
    blocked_days = cfg.get("blocked_days", [])
    stop_cap     = cfg.get("stop_pct_cap", 0.50)
    min_rr       = cfg.get("min_rr", MIN_RR)
    be_trigger   = cfg.get("be_trigger", BE_TRIGGER)

    dow = feat["dow"]
    if dow >= 5:
        log("  Weekend — no trade"); return None
    if dow in blocked_days:
        log(f"  Day {dow} blocked in config"); return None

    weekly_bear = trend.get("weekly_bear")
    daily_bear  = trend.get("daily_bear")

    # Insufficient trend data — fall back to intraday only with lower conviction
    trend_data_ok = weekly_bear is not None and daily_bear is not None

    # ── 3-timeframe direction ─────────────────────────────────────────────────
    intra_bear = feat["ema_bear"]   # mandatory intraday gate for PE
    intra_bull = feat["ema_bull"]   # mandatory intraday gate for CE

    direction = None
    all_bear = trend_data_ok and weekly_bear and daily_bear and intra_bear
    all_bull = trend_data_ok and (not weekly_bear) and (not daily_bear) and intra_bull

    if all_bear and feat["below_vwap30"] and pe_active:
        direction = "PE"
    elif all_bull and feat["above_vwap30"] and ce_active:
        direction = "CE"
    else:
        reasons = []
        if trend_data_ok:
            if not (weekly_bear if direction == "PE" or direction is None else not weekly_bear):
                reasons.append("weekly trend mismatch")
            if not (daily_bear if direction == "PE" or direction is None else not daily_bear):
                reasons.append("daily trend mismatch")
        if not intra_bear and not intra_bull:
            reasons.append("intraday EMA flat")
        log(f"  3-timeframe not aligned — SKIP ({'; '.join(reasons) or 'conflict'})")
        return None

    # ── Intraday mandatory gate ───────────────────────────────────────────────
    if direction == "PE" and not intra_bear:
        log("  ema_bear=False — mandatory PE gate — SKIP"); return None
    if direction == "CE" and not intra_bull:
        log("  ema_bull=False — mandatory CE gate — SKIP"); return None

    # ── Dynamic target from OR range ──────────────────────────────────────────
    or_rng = feat["OR_rng"]
    buckets = cfg.get("target_or_buckets", _DEFAULT_CFG["target_or_buckets"])
    if or_rng < 80:
        tgt_pct = buckets.get("lt80", 0.35)
    elif or_rng < 130:
        tgt_pct = buckets.get("lt130", 0.55)
    elif or_rng < 200:
        tgt_pct = buckets.get("lt200", 0.75)
    else:
        log(f"  OR range {or_rng:.0f} >= 200 — too wide, chaotic — SKIP"); return None

    # ── Adaptive stop at OR boundary ──────────────────────────────────────────
    entry_spot = feat["close30"]
    entry_prem = max(30.0, entry_spot * 0.007)   # ~0.7% ATM estimate

    or_boundary = feat["OR_H"] if direction == "PE" else feat["OR_L"]
    dist = (or_boundary - entry_spot) if direction == "PE" else (entry_spot - or_boundary)

    if dist <= 0:
        log(f"  Price already past OR boundary ({or_boundary:.0f}) — thesis invalid — SKIP")
        return None

    stp_pct = min((dist * DELTA) / entry_prem, stop_cap)

    # ── R:R gate ──────────────────────────────────────────────────────────────
    rr = tgt_pct / stp_pct
    if rr < min_rr:
        log(f"  R:R={rr:.2f} < {min_rr} — SKIP"); return None

    # ── Conviction score → lots ───────────────────────────────────────────────
    pe_hq = cfg.get("pe_hq_boosters", _DEFAULT_CFG["pe_hq_boosters"])
    ce_hq = cfg.get("ce_hq_boosters", _DEFAULT_CFG["ce_hq_boosters"])
    hq_keys = pe_hq if direction == "PE" else ce_hq
    n_hq = sum(1 for k in hq_keys if feat.get(k))

    score = 0
    if trend_data_ok:
        if direction == "PE":
            if weekly_bear: score += 20
            if daily_bear:  score += 20
        else:
            if not weekly_bear: score += 20
            if not daily_bear:  score += 20
    score += 20   # intraday EMA aligned (already gated above)
    score += 20 if n_hq >= 2 else (10 if n_hq == 1 else 0)
    if 80 <= or_rng <= 150: score += 10
    if abs(feat.get("vwap_dist_pct", 0)) >= 0.15: score += 10

    conv_lots = cfg.get("conviction_lots", {"80": 3, "60": 2, "40": 1})
    if score >= 80:   signal_lots = int(conv_lots.get("80", 3))
    elif score >= 60: signal_lots = int(conv_lots.get("60", 2))
    elif score >= 40: signal_lots = int(conv_lots.get("40", 1))
    else:
        log(f"  Conviction score {score} < 40 — SKIP"); return None

    boosters_hit = [k for k in hq_keys if feat.get(k)]

    log(f"  VR20 SIGNAL: {direction} | score={score} | R:R={rr:.1f} "
        f"| tgt={tgt_pct:.0%} stp={stp_pct:.0%} | {signal_lots}L "
        f"| boosters={boosters_hit}")

    return {
        "direction":    direction,
        "lots":         signal_lots,
        "score":        score,
        "target_pct":   round(tgt_pct, 3),
        "stop_pct":     round(stp_pct, 3),
        "be_trigger":   be_trigger,
        "rr":           round(rr, 2),
        "or_boundary":  or_boundary,
        "boosters":     boosters_hit,
        "weekly_bear":  weekly_bear,
        "daily_bear":   daily_bear,
        "entry_prem_est": round(entry_prem, 1),
    }

# ── Option helpers ────────────────────────────────────────────────────────────
def next_expiry() -> date:
    d = datetime.now(IST).date()
    delta = (EXPIRY_DOW - d.weekday()) % 7
    return d + timedelta(days=delta)

def atm_strike(spot: float) -> int:
    return round(spot / ATM_STEP) * ATM_STEP

def _is_monthly_expiry(exp: date) -> bool:
    return (exp + timedelta(days=7)).month != exp.month

def opt_sym(exp: date, strike: int, opt: str) -> str:
    yy = exp.year % 100
    if INDEX_NAME in ("BANKNIFTY", "FINNIFTY") or _is_monthly_expiry(exp):
        mon = exp.strftime("%b").upper()
        return f"{INDEX_NAME}{yy:02d}{mon}{strike}{opt}"
    return f"{INDEX_NAME}{yy:02d}{exp.month}{exp.day:02d}{strike}{opt}"

def get_ltp() -> float | None:
    try:
        g = _client()
        r = g.get_ltp(trading_symbol=INDEX_NAME, exchange="NSE",
                      segment=g.SEGMENT_CASH)
        if isinstance(r, dict):
            return float(r.get("ltp") or r.get("last_price") or 0) or None
    except Exception:
        pass
    return None

def compute_lots(premium: float, requested: int) -> int:
    usable = CAPITAL * DEPLOY
    cost   = premium * LOT_SIZE
    afford = max(1, int(usable / cost))
    return min(requested, afford, 3)

# ── Order helpers ─────────────────────────────────────────────────────────────
def _place(sym, txn, qty):
    try:
        g = _client()
        return g.place_order(
            trading_symbol=sym, exchange="NSE",
            segment=g.SEGMENT_FNO, transaction_type=txn,
            order_type=g.ORDER_TYPE_MARKET,
            quantity=qty, product=g.PRODUCT_MIS,
            validity=g.VALIDITY_DAY, price=0.0)
    except Exception as e:
        log(f"  Order error: {e}"); return None

def enter(direction: str, lots: int, spot: float) -> tuple | None:
    exp    = next_expiry()
    strike = atm_strike(spot)
    sym    = opt_sym(exp, strike, direction)
    shares = lots * LOT_SIZE
    log(f"  BUY {sym} x{shares} (PAPER={PAPER_MODE})")
    if not PAPER_MODE:
        r = _place(sym, _client().__class__.TRANSACTION_TYPE_BUY, shares)
        if not r:
            return None
    prem_est = max(30.0, spot * 0.007)
    tg(f"SIGNAL {direction} {strike} | {lots}L | spot {spot:.0f} | est prem {prem_est:.0f} "
       f"| {'PAPER' if PAPER_MODE else 'LIVE'}")
    return sym, prem_est

def exit_pos(sym: str, lots: int):
    if not PAPER_MODE:
        _place(sym, _client().__class__.TRANSACTION_TYPE_SELL, lots * LOT_SIZE)

# ── Position monitor (VR20-specific: 11:30 tighten, 12:30 hard exit) ──────────
async def monitor(sym: str, direction: str, lots: int,
                  entry_prem: float, entry_spot: float,
                  stop_pct: float, target_pct: float, be_trigger: float,
                  signal: dict) -> float:

    dir_sign  = 1 if direction == "CE" else -1
    stop      = entry_prem * (1 - stop_pct)
    target    = entry_prem * (1 + target_pct)
    be_prem   = entry_prem * be_trigger
    remaining = lots
    booked    = 0.0
    be_moved  = False
    time_tightened = False
    loop      = asyncio.get_event_loop()
    ex        = ThreadPoolExecutor(1)
    journal_data = {
        "time_stop_used": False,
        "be_trail_fired": False,
        "be_trail_time":  None,
    }

    log(f"  Monitor {direction} | entry_prem={entry_prem:.1f} "
        f"stop={stop:.1f}({stop_pct:.0%}) target={target:.1f}({target_pct:.0%}) "
        f"be_trigger={be_prem:.1f} | {remaining}L")

    while remaining > 0:
        now = datetime.now(IST)
        h, m = now.hour, now.minute

        # ── Hard exit at 12:30 ─────────────────────────────────────────────
        if (h, m) >= TIME_EXIT:
            spot = await loop.run_in_executor(ex, get_ltp) or entry_spot
            move = (spot - entry_spot) * dir_sign
            prem = max(5.0, entry_prem + DELTA * move)
            pnl  = (prem - entry_prem) * remaining * LOT_SIZE
            exit_pos(sym, remaining)
            booked += pnl; remaining = 0
            outcome = "TIME"
            log(f"  TIME EXIT 12:30 | prem={prem:.1f} | P&L~₹{booked:+,.0f}")
            tg(f"TIME EXIT | {direction} | prem {prem:.0f} | P&L ₹{booked:+,.0f}")
            _write_journal(signal, entry_spot, spot, prem, entry_prem, outcome, booked, journal_data)
            break

        spot = await loop.run_in_executor(ex, get_ltp)
        if not spot:
            await asyncio.sleep(15); continue

        move = (spot - entry_spot) * dir_sign
        prem = max(5.0, entry_prem + DELTA * move)

        # ── Breakeven trail (+25%) ─────────────────────────────────────────
        if not be_moved and prem >= be_prem:
            stop = entry_prem
            be_moved = True
            journal_data["be_trail_fired"] = True
            journal_data["be_trail_time"]  = now.strftime("%H:%M")
            log(f"  BREAKEVEN trail fired at {now.strftime('%H:%M')} | stop → entry {entry_prem:.1f}")

        # ── 11:30 time tighten ─────────────────────────────────────────────
        if not time_tightened and (h, m) >= TIME_TIGHTEN:
            if prem < entry_prem and not be_moved:
                stop = entry_prem   # force breakeven stop
                be_moved = True
                time_tightened = True
                journal_data["time_stop_used"] = True
                log(f"  11:30 TIME TIGHTEN — underwater, stop → entry {entry_prem:.1f}")
            time_tightened = True

        # ── Stop check ────────────────────────────────────────────────────
        if prem <= stop:
            pnl = (prem - entry_prem) * remaining * LOT_SIZE
            exit_pos(sym, remaining)
            booked += pnl; remaining = 0
            outcome = "BREAKEVEN" if abs(prem - entry_prem) < 2 else "STOP"
            log(f"  {outcome} | prem={prem:.1f} | P&L~₹{booked:+,.0f}")
            tg(f"{outcome} | {direction} | prem {prem:.0f} | P&L ₹{booked:+,.0f}")
            _write_journal(signal, entry_spot, spot, prem, entry_prem, outcome, booked, journal_data)
            break

        # ── Target check ──────────────────────────────────────────────────
        if prem >= target:
            pnl = (prem - entry_prem) * remaining * LOT_SIZE
            exit_pos(sym, remaining)
            booked += pnl; remaining = 0
            outcome = "TARGET"
            log(f"  TARGET +{target_pct:.0%} | prem={prem:.1f} | P&L~₹{booked:+,.0f}")
            tg(f"TARGET +{target_pct:.0%} | {direction} | prem {prem:.0f} | P&L ₹{booked:+,.0f}")
            _write_journal(signal, entry_spot, spot, prem, entry_prem, outcome, booked, journal_data)
            break

        await asyncio.sleep(20)

    return booked

# ── Journal write ─────────────────────────────────────────────────────────────
def _write_journal(signal: dict, entry_spot: float, exit_spot: float,
                   exit_prem: float, entry_prem: float,
                   outcome: str, pnl: float, journal_data: dict):
    """Delegate to vr20_journal.py if available. Log locally always."""
    now = datetime.now(IST)
    row = {
        "date":         now.strftime("%Y-%m-%d"),
        "day":          now.strftime("%a"),
        "direction":    signal["direction"],
        "entry_time":   "09:44",
        "entry_spot":   entry_spot,
        "or_h":         signal.get("or_boundary") if signal["direction"]=="PE" else None,
        "or_l":         signal.get("or_boundary") if signal["direction"]=="CE" else None,
        "or_rng":       None,  # filled by caller context
        "stop_spot":    signal.get("or_boundary"),
        "target_spot":  None,
        "rr":           signal["rr"],
        "or_bucket":    ("S" if signal.get("or_rng",100)<80 else
                         "M" if signal.get("or_rng",100)<130 else "L"),
        "weekly_trend": "BEAR" if signal.get("weekly_bear") else "BULL",
        "daily_trend":  "BEAR" if signal.get("daily_bear") else "BULL",
        "intra_ema":    "bear" if signal["direction"]=="PE" else "bull",
        "vwap_dist":    None,
        "stop_logic":   "OR_H" if signal["direction"]=="PE" else "OR_L",
        "lots":         signal["lots"],
        "time_stop":    "Y" if journal_data.get("time_stop_used") else "N",
        "be_trail":     f"Y@{journal_data['be_trail_time']}" if journal_data.get("be_trail_fired") else "N",
        "score":        signal["score"],
        "boosters":     ",".join(signal.get("boosters", [])),
        "exit_time":    now.strftime("%H:%M"),
        "exit_spot":    exit_spot,
        "outcome":      outcome,
        "prem_pts":     round(exit_prem - entry_prem, 1),
        "pnl":          round(pnl, 0),
    }
    log(f"  Journal: {outcome} | ₹{pnl:+,.0f} | score={signal['score']} | R:R={signal['rr']}")

    # Try to write to Google Sheets
    journal_py = Path(__file__).parent / "vr20_journal.py"
    if journal_py.exists():
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("vr20_journal", journal_py)
            jmod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(jmod)
            jmod.append_row(row)
            log("  Journal row written to Google Sheets")
        except Exception as e:
            log(f"  Journal write failed (non-fatal): {e}")

# ── Data fetch ────────────────────────────────────────────────────────────────
async def wait_until(h: int, m: int):
    while True:
        now = datetime.now(IST)
        if now.hour > h or (now.hour == h and now.minute >= m):
            return
        await asyncio.sleep(10)

def fetch_upto_now() -> dict | None:
    """Fetch today's 1-min OHLCV up to current time."""
    try:
        g   = _client()
        now = datetime.now(IST)
        res = g.get_historical_data(
            trading_symbol=INDEX_NAME, exchange="NSE",
            segment=g.SEGMENT_CASH, interval="1m",
            from_date=now.replace(hour=9, minute=15, second=0, microsecond=0),
            to_date=now)
        if not res or "candles" not in res:
            return None
        candles = res["candles"]
        if not candles:
            return None
        return {
            "o": [float(c[1]) for c in candles],
            "h": [float(c[2]) for c in candles],
            "l": [float(c[3]) for c in candles],
            "c": [float(c[4]) for c in candles],
            "v": [float(c[5]) for c in candles],
        }
    except Exception as e:
        log(f"  fetch_upto_now error: {e}"); return None

def _ensure_token():
    try:
        import subprocess
        r = subprocess.run(
            ["python3", str(Path(__file__).parent / "refresh_token.py")],
            capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            _reload_env()
    except Exception as e:
        log(f"  Token refresh failed: {e}")

# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    today = datetime.now(IST).date()
    dow   = today.weekday()
    dname = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][dow]

    log("=" * 60)
    log(f"VR20 Strategy  |  {today}  |  {dname}  |  {INDEX_NAME}")
    log("=" * 60)

    _ensure_token()

    if dow >= 5:
        log("Weekend — skipping"); return

    # Print config
    cfg = load_config()
    log(f"Config: PE={cfg['pe_active']} CE={cfg['ce_active']} "
        f"| min_rr={cfg['min_rr']} | be={cfg['be_trigger']} "
        f"| OR buckets={cfg['target_or_buckets']}")

    # Pause flag
    if (Path(__file__).parent / "vr20_pause.flag").exists():
        msg = "VR20 PAUSED — skipping today"
        log(msg); tg(msg); return

    now = datetime.now(IST)
    if now.hour >= 12:
        log("Past entry window — no trade"); return

    # Wait until 9:44 (signal candle closes)
    if now.hour < 9 or (now.hour == 9 and now.minute < 44):
        log("Waiting for 9:44 signal candle...")
        await wait_until(9, 44)

    _ensure_token()
    _reload_env()

    # ── Fetch today's data up to 9:44 ────────────────────────────────────────
    log("Fetching 9:15–9:44 data...")
    data = fetch_upto_now()
    if not data or len(data["c"]) < B30:
        log("Insufficient data — skip")
        tg(f"No data at 9:44 — skip"); return

    # ── Load cache for trend computation ─────────────────────────────────────
    cache = {}
    if CACHE_F.exists():
        try:
            cache = json.loads(CACHE_F.read_text())
        except Exception:
            pass

    today_str = str(today)
    trend = compute_trend(cache, today_str, float(data["o"][0]))
    log(f"  Weekly: {'BEAR' if trend['weekly_bear'] else 'BULL'} (prev_close={trend['prev_close']} w_ema={trend['w_ema']}) "
        f"| Daily: {'BEAR' if trend['daily_bear'] else 'BULL'} (open={data['o'][0]:.0f} d_ema={trend['d_ema']})")

    # Previous day data for features
    prev = None
    for k in sorted(cache.keys(), reverse=True):
        if k < today_str:
            prev = cache[k]; break

    feat = compute_features(data, prev, today)
    log(f"  VWAP={feat['vwap30']:.1f} close={feat['close30']:.1f} "
        f"below={feat['below_vwap30']} OR_rng={feat['OR_rng']:.0f} "
        f"ema_bear={feat['ema_bear']} orb_up={feat['orb_up']} "
        f"gap={feat['gap']:+.0f} fri={feat['is_friday']}")

    signal = evaluate_signal(feat, trend)

    if not signal:
        log("No VR20 signal today")
        tg(f"No signal | VWAP={'below' if feat['below_vwap30'] else 'above'} "
           f"OR={feat['OR_rng']:.0f}pts")
        return

    direction = signal["direction"]
    lots      = signal["lots"]
    entry_spot = feat["close30"]

    # Compute actual lot count against capital
    entry_prem = signal["entry_prem_est"]
    lots = compute_lots(entry_prem, lots)
    signal["lots"] = lots   # update for journal

    # Also store some feat data in signal for journal
    signal["or_rng"] = feat["OR_rng"]
    signal["vwap_dist_pct"] = feat["vwap_dist_pct"]

    tg(f"SIGNAL {direction} | score={signal['score']} R:R={signal['rr']} "
       f"tgt={signal['target_pct']:.0%} stp={signal['stop_pct']:.0%} "
       f"OR={feat['OR_rng']:.0f}pts {lots}L | {','.join(signal['boosters']) or 'trend-only'}")

    # Enter
    result = enter(direction, lots, entry_spot)
    if not result:
        log("Order failed — skip"); tg("Order failed"); return

    sym, entry_prem_actual = result
    entry_prem = entry_prem_actual

    # Monitor
    pnl = await monitor(
        sym=sym, direction=direction, lots=lots,
        entry_prem=entry_prem, entry_spot=entry_spot,
        stop_pct=signal["stop_pct"], target_pct=signal["target_pct"],
        be_trigger=signal["be_trigger"], signal=signal)

    log(f"VR20 session complete | Net P&L~₹{pnl:+,.0f}")

if __name__ == "__main__":
    asyncio.run(main())
