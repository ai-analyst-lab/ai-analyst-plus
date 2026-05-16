"""
vr20_journal.py  —  Google Sheets trade journal for VR20

Setup (one-time):
  1. Create a Google Service Account → download credentials JSON
  2. Copy to ~/groww-bot/vr20_sa_credentials.json
  3. Create a Google Sheet named "VR20 Trade Journal"
  4. Share the sheet with the service account email (Editor)
  5. Set SHEET_NAME below if you used a different name

Called from vr20_bot.py on every trade close:
    from vr20_journal import append_trade
    append_trade(journal_row)

journal_row is a dict with keys matching the 31 column schema below.
Missing keys default to empty string — do not crash the bot.
"""

import json
import os
import traceback
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
SERVICE_ACCOUNT_FILE = BASE / "vr20_sa_credentials.json"
SHEET_NAME = "VR20 Trade Journal"
WORKSHEET_NAME = "Trades"           # first sheet tab
WEEKLY_WORKSHEET = "Weekly Summary" # second sheet tab

# Column order matches spec §7.2 (A through AE = 31 cols)
COLUMNS = [
    "Date",             # A  - YYYY-MM-DD
    "Day",              # B  - Mon/Tue/.../Fri
    "Direction",        # C  - PE / CE
    "Entry Time",       # D  - HH:MM
    "Entry Spot",       # E  - spot price at entry
    "OR High",          # F
    "OR Low",           # G
    "OR Range",         # H  - OR High - OR Low
    "Stop Level",       # I  - spot price at stop (OR boundary)
    "Target Level",     # J  - target spot (computed)
    "R:R Ratio",        # K  - target_pct / stop_pct
    "OR Range Bucket",  # L  - S (<80) / M (80-129) / L (130-199)
    "Weekly Trend",     # M  - BULL / BEAR
    "Daily Trend",      # N  - BULL / BEAR
    "Intraday EMA",     # O  - bull / bear
    "Entry Quality",    # P  - VWAP distance %
    "Stop Logic",       # Q  - OR_HIGH / OR_LOW / capped
    "Lots",             # R  - 1 / 2 / 3
    "Time Stop Used",   # S  - Y / N
    "BE Trail Fired",   # T  - N / HH:MM
    "Conviction Score", # U  - 0–100
    "Boosters Hit",     # V  - comma-separated
    "Exit Time",        # W  - HH:MM
    "Exit Spot",        # X
    "Outcome",          # Y  - TARGET / STOP / TIME / BREAKEVEN
    "Premium Pts",      # Z  - gain/loss in premium points
    "P&L (INR)",        # AA - ₹ amount
    "Cumulative P&L",   # AB - running total (formula in sheet)
    "What Worked",      # AC - manual
    "What Didn't",      # AD - manual
    "Action Next Trade",# AE - manual
]

_sheet_cache = None  # worksheet object cached after first connect


def _connect():
    """Open the Trades worksheet, creating header row if blank."""
    global _sheet_cache
    if _sheet_cache is not None:
        return _sheet_cache

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        raise RuntimeError("gspread not installed — run: pip3 install gspread google-auth")

    if not SERVICE_ACCOUNT_FILE.exists():
        raise FileNotFoundError(
            f"Service account credentials not found at {SERVICE_ACCOUNT_FILE}\n"
            "Download from Google Cloud Console → IAM → Service Accounts → Keys."
        )

    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(str(SERVICE_ACCOUNT_FILE), scopes=scopes)
    gc = gspread.authorize(creds)

    try:
        sh = gc.open(SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        raise RuntimeError(
            f"Google Sheet '{SHEET_NAME}' not found.\n"
            "Create it, share it with the service account email, and try again."
        )

    # Trades tab
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=2000, cols=len(COLUMNS) + 2)

    # Write header if sheet is empty
    if ws.acell("A1").value != "Date":
        ws.insert_row(COLUMNS, index=1)
        # Freeze header
        sh.batch_update({
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": ws.id,
                        "gridProperties": {"frozenRowCount": 1}
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            }]
        })
        # AB column: running cumulative formula (starts row 2)
        # We'll add it dynamically as rows are appended

    _sheet_cache = ws
    return ws


def _cumulative_formula(row: int) -> str:
    """Return a SUM formula for cumulative P&L up to this row."""
    # AA column = index 27 (1-based) → column letter = AA
    return f"=SUM($AA$2:$AA{row})"


def append_trade(data: dict) -> bool:
    """
    Append one trade row to the Trades worksheet.

    Args:
        data: dict with keys matching COLUMNS (unknown keys ignored,
              missing keys default to "").

    Returns:
        True on success, False on any error (never raises — must not crash bot).
    """
    try:
        ws = _connect()
        next_row = len(ws.get_all_values()) + 1  # 1-based, after header

        row = []
        for col in COLUMNS:
            val = data.get(col, "")
            # AB (Cumulative P&L) is a formula
            if col == "Cumulative P&L":
                val = _cumulative_formula(next_row)
            row.append(val)

        ws.append_row(row, value_input_option="USER_ENTERED")

        # Color-code outcome cell (Y column = index 25, 1-based = 25)
        outcome = data.get("Outcome", "")
        _color_outcome_cell(ws, next_row, outcome)

        return True

    except Exception:
        # Journal failure MUST NOT crash the bot
        traceback.print_exc()
        return False


def _color_outcome_cell(ws, row: int, outcome: str):
    """Apply background color to the Outcome cell based on result."""
    color_map = {
        "TARGET":    {"red": 0.78, "green": 0.91, "blue": 0.78},   # light green
        "BREAKEVEN": {"red": 0.93, "green": 0.93, "blue": 0.93},   # light gray
        "TIME":      {"red": 1.0,  "green": 0.95, "blue": 0.8},    # light amber
        "STOP":      {"red": 0.96, "green": 0.78, "blue": 0.78},   # light red
    }
    color = color_map.get(outcome)
    if not color:
        return
    try:
        # Y column = 25th column = col index 24 (0-based)
        col_index = COLUMNS.index("Outcome")  # 0-based
        col_letter = _col_letter(col_index + 1)
        cell_addr = f"{col_letter}{row}"
        ws.format(cell_addr, {
            "backgroundColor": color,
            "textFormat": {"bold": True}
        })
    except Exception:
        pass  # formatting is cosmetic — ignore failures


def _col_letter(n: int) -> str:
    """Convert 1-based column number to A-Z/AA-AZ letter."""
    result = ""
    while n:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def build_row(
    *,
    date: str,
    day: str,
    direction: str,
    entry_time: str,
    entry_spot: float,
    or_high: float,
    or_low: float,
    or_range: float,
    stop_level: float,
    target_level: float,
    rr_ratio: float,
    or_bucket: str,
    weekly_trend: str,
    daily_trend: str,
    intraday_ema: str,
    entry_quality: float,
    stop_logic: str,
    lots: int,
    time_stop_used: bool,
    be_trail_fired,  # False or "HH:MM"
    conviction_score: int,
    boosters_hit: list,
    exit_time: str,
    exit_spot: float,
    outcome: str,
    premium_pts: float,
    pnl_inr: float,
) -> dict:
    """
    Convenience constructor so callers don't have to match exact column strings.
    Returns a dict ready for append_trade().
    """
    return {
        "Date": date,
        "Day": day,
        "Direction": direction,
        "Entry Time": entry_time,
        "Entry Spot": round(entry_spot, 2),
        "OR High": round(or_high, 2),
        "OR Low": round(or_low, 2),
        "OR Range": round(or_range, 1),
        "Stop Level": round(stop_level, 2),
        "Target Level": round(target_level, 2),
        "R:R Ratio": round(rr_ratio, 2),
        "OR Range Bucket": or_bucket,
        "Weekly Trend": weekly_trend,
        "Daily Trend": daily_trend,
        "Intraday EMA": intraday_ema,
        "Entry Quality": f"{entry_quality:.3f}",
        "Stop Logic": stop_logic,
        "Lots": lots,
        "Time Stop Used": "Y" if time_stop_used else "N",
        "BE Trail Fired": str(be_trail_fired) if be_trail_fired else "N",
        "Conviction Score": conviction_score,
        "Boosters Hit": ", ".join(boosters_hit),
        "Exit Time": exit_time,
        "Exit Spot": round(exit_spot, 2),
        "Outcome": outcome,
        "Premium Pts": round(premium_pts, 2),
        "P&L (INR)": round(pnl_inr, 0),
        "Cumulative P&L": "",   # filled by append_trade with formula
        "What Worked": "",
        "What Didn't": "",
        "Action Next Trade": "",
    }


# ── Weekly Summary sheet setup ─────────────────────────────────────────────────

def setup_weekly_summary(spreadsheet_id: str = None):
    """
    Create or refresh the Weekly Summary sheet with auto-computed formulas.
    Call once after first trade, or after clearing the Trades sheet.

    This is informational — the formulas reference the Trades sheet columns.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(str(SERVICE_ACCOUNT_FILE), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open(SHEET_NAME)

        try:
            ws = sh.worksheet(WEEKLY_WORKSHEET)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=WEEKLY_WORKSHEET, rows=100, cols=10)

        # Summary formulas referencing Trades sheet
        header = ["Metric", "Value"]
        rows = [
            header,
            ["Total Trades", f"=COUNTA(Trades!A2:A)"],
            ["Win Rate",     f"=COUNTIF(Trades!Y2:Y,\"TARGET\")/COUNTA(Trades!Y2:Y)"],
            ["Stop Rate",    f"=COUNTIF(Trades!Y2:Y,\"STOP\")/COUNTA(Trades!Y2:Y)"],
            ["BE Rate",      f"=COUNTIF(Trades!Y2:Y,\"BREAKEVEN\")/COUNTA(Trades!Y2:Y)"],
            ["Time Rate",    f"=COUNTIF(Trades!Y2:Y,\"TIME\")/COUNTA(Trades!Y2:Y)"],
            ["Total P&L",    f"=SUM(Trades!AA2:AA)"],
            ["Avg P&L/Trade",f"=AVERAGE(Trades!AA2:AA)"],
            ["Best Trade",   f"=MAX(Trades!AA2:AA)"],
            ["Worst Trade",  f"=MIN(Trades!AA2:AA)"],
            ["Avg Conv Score",f"=AVERAGE(Trades!U2:U)"],
            ["Avg R:R",      f"=AVERAGE(Trades!K2:K)"],
            ["PE Trades",    f"=COUNTIF(Trades!C2:C,\"PE\")"],
            ["CE Trades",    f"=COUNTIF(Trades!C2:C,\"CE\")"],
        ]

        for i, row in enumerate(rows, start=1):
            ws.update(f"A{i}:B{i}", [row])

        print(f"Weekly Summary sheet set up in '{SHEET_NAME}'")
        return True

    except Exception:
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Quick smoke test — appends a dummy row
    print("Testing vr20_journal.py ...")
    test_row = build_row(
        date="2026-05-16", day="Fri", direction="PE",
        entry_time="09:44", entry_spot=24350.0,
        or_high=24420.0, or_low=24280.0, or_range=140.0,
        stop_level=24420.0, target_level=24090.0,
        rr_ratio=2.1, or_bucket="M",
        weekly_trend="BEAR", daily_trend="BEAR", intraday_ema="bear",
        entry_quality=0.18, stop_logic="OR_HIGH",
        lots=2, time_stop_used=False,
        be_trail_fired=False, conviction_score=70,
        boosters_hit=["orb_up", "is_friday"],
        exit_time="10:45", exit_spot=24090.0,
        outcome="TARGET", premium_pts=95.2, pnl_inr=8568.0,
    )
    ok = append_trade(test_row)
    print("append_trade:", "OK" if ok else "FAILED — check credentials")
