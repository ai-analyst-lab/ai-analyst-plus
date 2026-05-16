#!/usr/bin/env python3
"""Multi-user bot runner.
Usage:
  python3 multi_runner.py --mode vr10       # 09:15 IST — runs vr10_bot.py for all users
  python3 multi_runner.py --mode vr20       # 09:15 IST — runs vr20_bot.py for all users (parallel validation)
  python3 multi_runner.py --mode ml         # 11:01 IST — runs momentum_lock_bot.py for all users
  python3 multi_runner.py --mode eod        # 15:35 IST — sends consolidated EOD summary
"""
import json, os, re, subprocess, sys, threading, time, argparse
from pathlib import Path
from datetime import datetime, date
import pytz

IST     = pytz.timezone("Asia/Kolkata")
BASE    = Path('/home/ubuntu/groww-bot')
USERS_F = BASE / 'users.json'
LOGS    = BASE / 'logs'
LOGS.mkdir(exist_ok=True)

# Load base env
_base_env = {**os.environ}
for line in (BASE / '.env').read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('=')
        _base_env.setdefault(k.strip(), v.strip())

def now_ist():
    return datetime.now(IST)

def tg_send(chat_id, msg):
    try:
        token = _base_env.get('TELEGRAM_TOKEN', '')
        import urllib.request, urllib.parse
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': msg}).encode()
        urllib.request.urlopen(
            f'https://api.telegram.org/bot{token}/sendMessage', data=data, timeout=8)
    except Exception:
        pass

def tg_admin(msg):
    tg_send(_base_env.get('TELEGRAM_CHAT_ID', ''), msg)

def load_users():
    return json.loads(USERS_F.read_text())

def save_users(users):
    USERS_F.write_text(json.dumps(users, indent=2))

def build_env(user):
    env = {**_base_env,
           'GROWW_ACCESS_TOKEN': user.get('access_token', ''),
           'TELEGRAM_CHAT_ID':   user.get('tg_chat', ''),
           'CAPITAL':            str(user.get('capital', 30000))}
    return env

def run_bot(user, index, script, log_suffix):
    today     = now_ist().date()
    log_path  = LOGS / f"{today}_{user['name']}_{index.lower()}_{log_suffix}.log"
    env       = build_env(user)
    cmd       = ['python3', '-u', str(BASE / script), '--index', index]

    with open(log_path, 'w') as lf:
        proc = subprocess.run(cmd, env=env, stdout=lf, stderr=subprocess.STDOUT,
                               cwd=str(BASE), timeout=28800)  # 8 hr max
    return log_path, proc.returncode

def parse_trade_from_log(log_path):
    """Extract key trade info from a bot log file."""
    result = {'traded': False, 'direction': None, 'strike': None,
              'entry': None, 'exit': None, 'pnl': None, 'status': 'No trade',
              'outcome': None}
    try:
        txt = log_path.read_text()
        m = re.search(r'SIGNAL[^\n]*(PE|CE)', txt)
        if m:
            result['traded'] = True
            result['direction'] = m.group(1)
        m = re.search(r'BUY \w*(\d{5,})(CE|PE)', txt)
        if m: result['strike'] = m.group(1)
        m = re.search(r'entry[=:]\s*([\d.]+)', txt)
        if m: result['entry'] = float(m.group(1))
        m = re.search(r'(?:STOP|TARGET)[^\n]*prem=([\d.]+)', txt)
        if m: result['exit'] = float(m.group(1))
        m = re.search(r'P&L\s*~?\s*Rs([+-]?[\d.]+)', txt)
        if m: result['pnl'] = float(m.group(1))
        for outcome in ('TARGET', 'BREAKEVEN', 'STOP', 'TIME'):
            if outcome in txt and result['traded']:
                result['outcome'] = outcome
                break
        if result['outcome'] == 'TARGET':    result['status'] = 'WIN'
        elif result['outcome'] == 'STOP':    result['status'] = 'LOSS'
        elif result['outcome'] == 'BREAKEVEN': result['status'] = 'BE'
        elif result['outcome'] == 'TIME':    result['status'] = 'TIME'
        elif result['traded']:               result['status'] = 'running'
    except Exception:
        pass
    return result

# ── VR10 mode ─────────────────────────────────────────────────────────────────

def mode_vr10():
    users   = load_users()
    threads = []

    for u in users:
        if u.get('paused', True):
            print(f"SKIP {u['display']} -- paused")
            continue
        if not u.get('access_token'):
            print(f"SKIP {u['display']} -- no token")
            continue
        for idx in u.get('vr10_indices', []):
            def _run(user=u, index=idx):
                print(f"START {user['display']} {index} VR10")
                log_path, rc = run_bot(user, index, 'vr10_bot.py', 'vr10')
                print(f"DONE  {user['display']} {index} VR10 (rc={rc})")
                trade = parse_trade_from_log(log_path)
                users_fresh = load_users()
                for uu in users_fresh:
                    if uu['name'] == user['name']:
                        uu.setdefault('today', {})[f"vr10_{index}"] = trade
                        break
                save_users(users_fresh)

            t = threading.Thread(target=_run, daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.3)

    for t in threads:
        t.join()
    print("All VR10 runners done.")

# ── VR20 mode ─────────────────────────────────────────────────────────────────

def mode_vr20():
    """Run vr20_bot.py for each user alongside VR10 (parallel validation)."""
    users   = load_users()
    threads = []

    for u in users:
        if u.get('paused', True):
            print(f"SKIP {u['display']} -- paused")
            continue
        if not u.get('access_token'):
            print(f"SKIP {u['display']} -- no token")
            continue
        # Fall back to vr10_indices if vr20_indices not configured
        indices = u.get('vr20_indices') or u.get('vr10_indices', [])
        for idx in indices:
            def _run(user=u, index=idx):
                print(f"START {user['display']} {index} VR20")
                log_path, rc = run_bot(user, index, 'vr20_bot.py', 'vr20')
                print(f"DONE  {user['display']} {index} VR20 (rc={rc})")
                trade = parse_trade_from_log(log_path)
                users_fresh = load_users()
                for uu in users_fresh:
                    if uu['name'] == user['name']:
                        uu.setdefault('today', {})[f"vr20_{index}"] = trade
                        break
                save_users(users_fresh)

            t = threading.Thread(target=_run, daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.3)

    for t in threads:
        t.join()
    print("All VR20 runners done.")

# ── ML mode ───────────────────────────────────────────────────────────────────

def mode_ml():
    users   = load_users()
    threads = []

    for u in users:
        if u.get('paused', True):
            print(f"SKIP {u['display']} -- paused")
            continue
        if not u.get('access_token'):
            print(f"SKIP {u['display']} -- no token")
            continue
        for idx in u.get('ml_indices', []):
            def _run(user=u, index=idx):
                print(f"START {user['display']} {index} ML")
                log_path, rc = run_bot(user, index, 'momentum_lock_bot.py', 'ml')
                print(f"DONE  {user['display']} {index} ML (rc={rc})")
                trade = parse_trade_from_log(log_path)
                users_fresh = load_users()
                for uu in users_fresh:
                    if uu['name'] == user['name']:
                        uu.setdefault('today', {})[f"ml_{index}"] = trade
                        break
                save_users(users_fresh)

            t = threading.Thread(target=_run, daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.3)

    for t in threads:
        t.join()
    print("All ML runners done.")

# ── EOD mode ──────────────────────────────────────────────────────────────────

def _format_trade_line(prefix, t):
    if not t or not t.get('traded'):
        return f"{prefix}: no trade"
    direction = t.get('direction', '?')
    outcome   = t.get('outcome') or 'running'
    pnl       = t.get('pnl') or 0
    return f"{prefix}: {direction} -- {outcome} -- Rs{pnl:+,.0f}"

def _agent_blurb(index):
    aglog_map = {
        "NIFTY":     BASE / "agent_decisions.json",
        "BANKNIFTY": BASE / "agent_decisions_banknifty.json",
        "FINNIFTY":  BASE / "agent_decisions_finnifty.json",
    }
    fp = aglog_map.get(index)
    if not fp or not fp.exists():
        return ""
    try:
        decisions = json.loads(fp.read_text())
        if not decisions:
            return ""
        latest = decisions[-1]
        if latest.get("date") != str(now_ist().date()):
            return ""
        a      = latest.get("analyses", {})
        regime = a.get("regime", "")
        m      = re.search(r"-> (\w+)", regime)
        label  = m.group(1) if m else "?"
        streak = a.get("streak", "")
        boosters = a.get("boosters", [])
        n_chg  = sum(1 for b in boosters if isinstance(b, dict) and b.get("action") not in ("keep", None))
        suffix = f", {n_chg} change(s)" if n_chg else ", no changes"
        return f"   {index}: {label} | {streak}{suffix}"
    except Exception:
        return ""

def mode_eod():
    users         = load_users()
    date_str      = now_ist().strftime('%d-%b')
    lines         = [f"EOD | {date_str}\n"]
    total_pnl_all = 0

    for u in users:
        status_tag = "PAUSED" if u.get('paused') else "ACTIVE"
        lines.append("-" * 30)
        lines.append(f"{u['display']}  |  {status_tag}")

        trades     = u.get('today', {}) or {}
        user_pnl   = 0
        traded_any = False

        # Gather all indices from all strategy keys
        indices = set()
        for key in trades:
            if '_' in key:
                indices.add(key.split('_', 1)[1].upper())

        for index in sorted(indices):
            vr10_t = trades.get(f"vr10_{index}")
            vr20_t = trades.get(f"vr20_{index}")
            ml_t   = trades.get(f"ml_{index}")

            if vr10_t or vr20_t or ml_t:
                lines.append(f"\n  {index}")
                if vr10_t:
                    traded_any = True
                    lines.append(f"  {_format_trade_line('VR10', vr10_t)}")
                    user_pnl += vr10_t.get('pnl') or 0
                if vr20_t:
                    traded_any = True
                    lines.append(f"  {_format_trade_line('VR20', vr20_t)}")
                    user_pnl += vr20_t.get('pnl') or 0
                if ml_t:
                    traded_any = True
                    lines.append(f"  {_format_trade_line('ML', ml_t)}")
                    user_pnl += ml_t.get('pnl') or 0

        if not traded_any:
            lines.append("  No trades today")
        else:
            lines.append(f"\n  Net P&L: Rs{user_pnl:+,.0f}")

        total_pnl_all += user_pnl

    lines.append("-" * 30)
    lines.append(f"Total P&L (all users): Rs{total_pnl_all:+,.0f}")

    agent_lines = [b for b in [_agent_blurb(i) for i in ["NIFTY", "BANKNIFTY", "FINNIFTY"]] if b]
    if agent_lines:
        lines.append("\nStrategy Agent")
        lines.extend(agent_lines)

    msg = "\n".join(lines)
    tg_admin(msg)
    print(msg)

    users_fresh = load_users()
    for u in users_fresh:
        u['today'] = {}
    save_users(users_fresh)


# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['vr10', 'vr20', 'ml', 'eod'], required=True)
    args = p.parse_args()

    if args.mode == 'vr10':   mode_vr10()
    elif args.mode == 'vr20': mode_vr20()
    elif args.mode == 'ml':   mode_ml()
    elif args.mode == 'eod':  mode_eod()
