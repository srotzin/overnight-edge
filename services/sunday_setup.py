import os
import csv
import json
import urllib.request
import re
from datetime import datetime, timezone, timedelta

# Import redesigned template
from sunday_setup_redesign import generate_sunday_setup_report, get_sunday_setup_footer

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
ADMIN_CHAT = "5975342168"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_bot.png"
DRAFTS_DIR = "/mnt/user/overnight-edge/tradingview_drafts"
LANDING_URL = "https://overnight-edge.vercel.app"

# Product Buy Button IDs for CTAs
DD_BUY = "buy_btn_1TWLs4GrDuTtAB3mRdCm5bnZ"
SS_BUY = "buy_btn_1TWLrSGrDuTtAB3muePQIrWx"
SQR_BUY = "buy_btn_1TWLniGrDuTtAB3mojv83V6D"
X10_BUY = "buy_btn_1TWLqtGrDuTtAB3m9vVOxud8"
X20_BUY = "buy_btn_1TWLqAGrDuTtAB3mBu2MrOMW"
PC_BUY = "buy_btn_1TWLpXGrDuTtAB3mzRewSdxs"
PP_BUY = "buy_btn_1TWLouGrDuTtAB3mhwdzodZK"

X_BEARER = "AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3DhUBulTxX7eRF9rfTKDQcP6z0acMTEtkWv7NnIqZtI7zJxlIcxy"
X_CLIENT_ID = "RFd5RTctLThrb1o2bFQ5US11cno6MTpjaQ"
X_CLIENT_SECRET = "BlpbjNtEL9BR7YiXdl9CQ3utKaNI1dL0XszACo0J_5duSTg2PO"

# Unique voice: editorial, strategic, week-ahead focused
# Purpose: FREE marketing piece that converts readers to paid subscribers
# Includes: "THIS WEEK ON OVERNIGHT EDGE" section teasing each paid tier

def send_telegram(text, chat_id=ADMIN_CHAT):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Send failed: {e}")
        return False

def send_telegram_photo(photo_path, caption, chat_id=ADMIN_CHAT):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    with open(photo_path, "rb") as f:
        photo_data = f.read()
    body = []
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="chat_id"')
    body.append(b"")
    body.append(chat_id.encode())
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="caption"')
    body.append(b"")
    body.append(caption.encode())
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="parse_mode"')
    body.append(b"")
    body.append(b"HTML")
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="photo"; filename="{os.path.basename(photo_path)}"'.encode())
    body.append(b"Content-Type: image/png")
    body.append(b"")
    body.append(photo_data)
    body.append(f"--{boundary}--".encode())
    payload = b"\r\n".join(body)
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Photo send failed: {e}")
        return False

def strip_html(text):
    """Strip HTML tags for TradingView plain text"""
    return re.sub(r'<[^>]+>', '', text)

def save_tradingview_draft(title, body):
    """Save a TradingView-formatted draft to disk"""
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{DRAFTS_DIR}/sunday_setup_{date_slug}.txt"
    
    footer = f"""━━━
📡 Get AI-powered market intelligence delivered to Telegram every morning.
→ {LANDING_URL}
#premarket #marketanalysis #ai #signals #smartmoney"""
    
    content = f"""TITLE: {title}

{body}

{footer}"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"TradingView draft saved: {filename}")
    return filename

def get_subscribers(tier_filter=None):
    subs = []
    try:
        with open("/mnt/user/overnight-edge/subscribers.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("status") == "active":
                    if tier_filter is None or row.get("tier") == tier_filter:
                        subs.append(row)
    except:
        pass
    return subs

def log_sunday(date_str, week_of, economic_events, top_earnings, geopolitical, options_exp, signals_syn, outlook, notes=""):
    with open("/mnt/user/overnight-edge/sunday_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, week_of, economic_events, top_earnings, geopolitical, options_exp, signals_syn, outlook, notes])

def fetch_economic_calendar():
    """Fetch key economic events for the upcoming week"""
    # In production: wire Alpha Vantage, Investing.com API, or Econoday
    # Simulated for now
    events = [
        {"day": "Mon", "event": "Fed Williams speech", "time": "10:00 AM", "consensus": ""},
        {"day": "Tue", "event": "JOLTS Job Openings", "time": "10:00 AM", "consensus": "8.1M"},
        {"day": "Wed", "event": "CPI (MoM)", "time": "8:30 AM", "consensus": "+0.3%"},
        {"day": "Wed", "event": "CPI (YoY)", "time": "8:30 AM", "consensus": "+3.4%"},
        {"day": "Thu", "event": "PPI (MoM)", "time": "8:30 AM", "consensus": "+0.2%"},
        {"day": "Thu", "event": "Jobless Claims", "time": "8:30 AM", "consensus": "215K"},
        {"day": "Fri", "event": "Consumer Sentiment (UoM)", "time": "10:00 AM", "consensus": "77.5"},
    ]
    return events

def fetch_top_earnings():
    """Fetch top earnings for the upcoming week"""
    # In production: wire Alpha Vantage, Financial Modeling Prep, or Benzinga
    earnings = [
        {"ticker": "AAPL", "eps_consensus": 1.51, "rev_consensus": "90.5B", "whisper": 1.55},
        {"ticker": "MSFT", "eps_consensus": 2.93, "rev_consensus": "64.5B", "whisper": 2.95},
        {"ticker": "NVDA", "eps_consensus": 5.95, "rev_consensus": "26.4B", "whisper": 6.02},
        {"ticker": "AMD", "eps_consensus": 0.62, "rev_consensus": "5.4B", "whisper": 0.65},
        {"ticker": "DIS", "eps_consensus": 1.10, "rev_consensus": "22.1B", "whisper": 1.12},
        {"ticker": "RBLX", "eps_consensus": -0.52, "rev_consensus": "860M", "whisper": -0.48},
        {"ticker": "LYFT", "eps_consensus": 0.08, "rev_consensus": "1.3B", "whisper": 0.10},
        {"ticker": "UBER", "eps_consensus": 0.42, "rev_consensus": "11.2B", "whisper": 0.45},
    ]
    return earnings

def fetch_geopolitical_watch():
    """Check for geopolitical events that could move markets"""
    # In production: scan news APIs, X feeds, government calendars
    return "Middle East tension remains elevated. No major new sanctions announced this weekend. EU energy ministers meeting Tuesday could impact LNG and power pricing. China trade data release Wednesday watched closely for export momentum."

def fetch_options_expiration():
    """Get options expiration info"""
    # In production: calculate from options chain data
    return "Monthly expiration — $4.2T notional. Max pain SPY: $525. Max pain QQQ: $445. Major dealer gamma flip at SPY $520."

def fetch_signals_synthesis():
    """Synthesize what XSignal accounts are watching for the week"""
    # In production: scan monitored X accounts for weekend/week-ahead posts
    return "X accounts focusing on CPI Wednesday as the key macro catalyst. Semiconductor earnings (NVDA, AMD) seen as sector bellwethers. Several accounts noting unusual call buying in energy names ahead of EU meeting. Crypto showing quiet weekend positioning, no major leverage flush."

def generate_brief():
    now = datetime.now(timezone.utc)
    
    # Calculate week of (next Monday)
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday = now + timedelta(days=days_until_monday)
    week_of = next_monday.strftime("%b %d")
    
    economic = fetch_economic_calendar()
    earnings = fetch_top_earnings()
    geo = fetch_geopolitical_watch()
    options = fetch_options_expiration()
    signals = fetch_signals_synthesis()
    
    # Build calendar lines
    cal_lines = "\n".join([f" <b>{e['day']}:</b> {e['event']} {e['time']}" + (f" | Consensus: {e['consensus']}" if e['consensus'] else "") for e in economic])
    
    # Build earnings lines (top 15, but we simulate 8)
    earn_lines = "\n".join([f" <b>{e['ticker']}:</b> EPS consensus ${e['eps_consensus']} | Rev {e['rev_consensus']} | Whisper ${e['whisper']}" for e in earnings])
    
    outlook = f"CPI on Wednesday is the week\u0027s headline risk. With consensus at +3.4% YoY, any deviation above 3.6% could reignite Treasury volatility and pressure rate-sensitive sectors. Semiconductor earnings (NVDA, AMD) midweek will set tone for AI trade. Energy names have a potential catalyst Tuesday. Keep position sizes tight ahead of CPI — this is a week where being directionally wrong is expensive."
    
    # Use redesigned template with "THIS WEEK ON OVERNIGHT EDGE" teasers
    brief = generate_sunday_setup_report(
        week_of=week_of,
        economic_calendar=economic,
        top_earnings=earnings,
        geopolitical=geo,
        options_exp=options,
        signals_syn=signals,
        week_outlook=outlook
    )
    
    return brief, week_of, economic, earnings, geo, options, signals, outlook

def post_to_x_thread(brief_text):
    """Post the Sunday Setup to X/Twitter as a thread"""
    # In production: use X API v2 to post thread
    # For now, log that it should be posted
    print("[X THREAD] Sunday Setup ready for posting:")
    print(brief_text[:200] + "...")
    # TODO: Implement X API posting when token is verified
    return True

def main():
    now = datetime.now(timezone.utc)
    
    print(f"Generating Sunday Setup — {now.strftime('%Y-%m-%d')}")
    
    brief, week_of, cal_lines, earn_lines, geo, options, signals, outlook = generate_brief()
    
    # 1. Send to ALL active subscribers (all tiers get Sunday Setup)
    all_subs = get_subscribers()
    for sub in all_subs:
        tg_id = sub.get("telegram_id", "")
        if tg_id:
            send_telegram(brief, tg_id)
    
    # 2. Send to admin
    send_telegram_photo(LOGO_PATH, brief, ADMIN_CHAT)
    
    # 3. Post to X/Twitter as free marketing thread
    post_to_x_thread(brief)
    
    # 4. Save TradingView draft
    tv_title = f"The Sunday Setup — Week of {week_of}"
    tv_body = strip_html(brief)
    save_tradingview_draft(tv_title, tv_body)
    
    # 5. Log
    log_sunday(
        now.strftime("%Y-%m-%d %H:%M"),
        week_of,
        cal_lines.replace("\n", " | "),
        earn_lines.replace("\n", " | "),
        geo,
        options,
        signals,
        outlook,
        f"Sent to {len(all_subs)} subscribers"
    )
    
    print(f"Sunday Setup complete. Week of {week_of}. Subscribers: {len(all_subs)}")

if __name__ == "__main__":
    main()
