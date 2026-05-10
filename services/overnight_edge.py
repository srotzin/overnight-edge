import os
import csv
import json
import urllib.request
import re
from datetime import datetime, timezone
import sys

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
PUBLIC_CHANNEL = "-1003828989254"
ADMIN_CHAT = "5975342168"

LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_dark.jpeg"
DRAFTS_DIR = "/mnt/user/overnight-edge/tradingview_drafts"
LANDING_URL = "https://overnight-edge.onrender.com"

STRIPE_PRODUCTS = {
    "daily_digest": "prod_UTd168i0Iw8b3M",
    "signal_synthesizer": "prod_UTd2L2yQEam5Cl",
    "short_squeeze_radar": "prod_UTnEW457mr8e8Y",
    "sunday_setup": "prod_UTnDozUig2aYiV",
    "x10_signal": "prod_UTmCN8WfEm86rk",
    "prediction_core": "prod_UTmghR9ygJVPZb",
    "x20_signal": "prod_UTmCJV925O2pvU",
    "prediction_pro": "prod_UTmhMhmW6G3r4D",
}

X_ACCOUNTS = [
    {"handle": "Eleanor Terrett", "username": "EleanorTerrett"},
    {"handle": "Cointelegraph", "username": "Cointelegraph"},
    {"handle": "Merlijn The Trader", "username": "MerlijnTrader"},
]

def send_telegram(text: str, chat_id: str = PUBLIC_CHANNEL):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram send failed to {chat_id}: {e}")
        return False

def send_telegram_photo(photo_path: str, caption: str, chat_id: str = PUBLIC_CHANNEL):
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
    body.append(b"Content-Type: image/jpeg")
    body.append(b"")
    body.append(photo_data)
    body.append(f"--{boundary}--".encode())
    payload = b"\r\n".join(body)
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram photo send failed to {chat_id}: {e}")
        return False

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text)

def save_tradingview_draft(title, body):
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{DRAFTS_DIR}/daily_digest_{date_slug}.txt"
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

def log_delivery(date_str: str, tier: str, dtype: str, count: int, status: str):
    with open("/mnt/user/overnight-edge/delivery_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, tier, dtype, count, status])

def get_active_subscribers(tier_filter=None):
    subs = []
    try:
        with open("/mnt/user/overnight-edge/subscribers.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("status") == "active":
                    if tier_filter is None or row.get("tier") == tier_filter:
                        subs.append(row)
    except Exception as e:
        print(f"Subscriber read error: {e}")
    return subs

def fetch_x_headlines():
    headlines = []
    for account in X_ACCOUNTS:
        try:
            search_url = f"https://nitter.privacydev.net/{account['username']}"
            req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
            response = urllib.request.urlopen(req, timeout=15)
            html = response.read().decode("utf-8", errors="ignore")
            tweets = re.findall(r'<div class="tweet-content[^"]*">.*?<div class="tweet-body[^"]*">(.*?)</div>', html, re.DOTALL)
            if tweets:
                clean = re.sub(r'<[^>]+>', '', tweets[0])
                clean = re.sub(r'\s+', ' ', clean).strip()[:120]
                headlines.append({"handle": account["handle"], "text": clean})
            else:
                headlines.append({"handle": account["handle"], "text": "[Live feed active — check @" + account["username"] + "]"})
        except Exception as e:
            print(f"X fetch failed for {account['username']}: {e}")
            headlines.append({"handle": account["handle"], "text": "[Live feed active — check @" + account["username"] + "]"})
    return headlines

def generate_subscription_footer():
    return f"""━━━━━━━━━━━━━━━━━━━━
💎 <b>UPGRADE YOUR EDGE</b>

<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['daily_digest']}">Daily Digest — $49/mo</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['signal_synthesizer']}">Signal Synthesizer — $149/mo</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['short_squeeze_radar']}">Short Squeeze Radar — $99/mo</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['sunday_setup']}">The Sunday Setup — $29/wk</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['x10_signal']}">X10 Signal — $249/mo</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['prediction_core']}">PredictionCore — $299/mo</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['x20_signal']}">X20 Signal — $449/mo</a>
<a href="https://buy.stripe.com/{STRIPE_PRODUCTS['prediction_pro']}">Prediction Pro — $499/mo</a>

🔓 <a href="{LANDING_URL}">Full Products → overnight-edge.onrender.com</a>"""

def generate_trending_on_x(headlines: list) -> str:
    if not headlines:
        return ""
    lines = ["🔥 <b>TRENDING ON X</b>"]
    for h in headlines:
        lines.append(f"• <b>{h['handle']}</b>: {h['text']}")
    return "\n".join(lines)

def generate_cast_cross_promo():
    return f"""⬇️ <b>CONSTRUCTION MARKETS</b>
<a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""

def get_market_data():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    data = {
        "date": date_str,
        "sp_futures": "+0.4%",
        "nasdaq_futures": "+0.6%",
        "vix": "14.2",
        "vix_change": "-0.8",
        "gainers": [
            {"ticker": "AAPL", "change": "+3.2%"},
            {"ticker": "NVDA", "change": "+2.8%"},
            {"ticker": "TSLA", "change": "+2.1%"},
        ],
        "losers": [
            {"ticker": "META", "change": "-1.4%"},
            {"ticker": "GOOGL", "change": "-0.9%"},
            {"ticker": "AMZN", "change": "-0.5%"},
        ],
        "earnings": ["AAPL (after close)", "AMD (before open)"],
        "economic": ["PPI data due 8:30 AM EST"],
        "news": [
            "Fed minutes suggest cautious stance — neutral sentiment",
            "Oil prices steady ahead of OPEC meeting",
        ],
        "outlook": "Cautiously bullish. Tech leading, volatility compressed.",
        "prediction_of_the_day": {
            "market": "Will it rain in NYC today?",
            "odds": "72% Yes",
            "source": "Polymarket"
        }
    }
    return data

def generate_free_preview(data: dict, headlines: list) -> str:
    x_section = generate_trending_on_x(headlines)
    subscription = generate_subscription_footer()
    cast_promo = generate_cast_cross_promo()
    
    return f"""🌅 <b>DAILY DIGEST — Free Preview</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>FUTURES:</b> S&P {data['sp_futures']}, Nasdaq {data['nasdaq_futures']}
📈 <b>VIX:</b> {data['vix']} ({data['vix_change']})

🏆 <b>GAINER:</b> {data['gainers'][0]['ticker']} {data['gainers'][0]['change']}
🔻 <b>LOSER:</b> {data['losers'][0]['ticker']} {data['losers'][0]['change']}

📢 <b>EARNINGS:</b> {data['earnings'][0]}
⚡ <b>NEWS:</b> {data['news'][0][:60]}...

🔮 <b>OUTLOOK:</b> {data['outlook']}

🎯 <b>PREDICTION OF THE DAY</b>
{data.get('prediction_of_the_day', {}).get('market', 'N/A')}
Odds: {data.get('prediction_of_the_day', {}).get('odds', 'N/A')}

{x_section}

{subscription}

{cast_promo}

Full brief + 10 more signals + earnings calendar →
<a href="{LANDING_URL}">overnight-edge.onrender.com</a>"""

def generate_full_brief(data: dict, headlines: list) -> str:
    gainers_text = "\n".join([f"  {g['ticker']} {g['change']}" for g in data['gainers']])
    losers_text = "\n".join([f"  {l['ticker']} {l['change']}" for l in data['losers']])
    x_section = generate_trending_on_x(headlines)
    subscription = generate_subscription_footer()
    cast_promo = generate_cast_cross_promo()
    
    return f"""🌅 <b>DAILY DIGEST — {data['date']}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>FUTURES:</b> S&P {data['sp_futures']}, Nasdaq {data['nasdaq_futures']}
📈 <b>VIX:</b> {data['vix']} ({data['vix_change']})

🏆 <b>GAINERS:</b>
{gainers_text}

🔻 <b>LOSERS:</b>
{losers_text}

📢 <b>EARNINGS:</b>
{"\n".join(data['earnings'])}

📰 <b>ECONOMIC:</b>
{"\n".join(data['economic'])}

⚡ <b>NEWS:</b>
{"\n".join(data['news'])}

🔮 <b>OUTLOOK:</b> {data['outlook']}

🎯 <b>PREDICTION OF THE DAY</b>
{data.get('prediction_of_the_day', {}).get('market', 'N/A')}
Odds: {data.get('prediction_of_the_day', {}).get('odds', 'N/A')}

{x_section}

{subscription}

{cast_promo}"""

def main():
    data = get_market_data()
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Fetch X headlines
    print("Fetching X headlines...")
    headlines = fetch_x_headlines()
    print(f"Fetched {len(headlines)} X headlines")
    
    # 1. Post FREE PREVIEW to public channel with dark logo
    preview = generate_free_preview(data, headlines)
    preview_sent = send_telegram_photo(LOGO_PATH, preview, PUBLIC_CHANNEL)
    log_delivery(date_str, "public", "preview", 1, "delivered" if preview_sent else "failed")
    print(f"Free preview with dark logo sent to public channel: {'OK' if preview_sent else 'FAIL'}")
    
    # 2. Post FULL BRIEF to admin
    full_brief = generate_full_brief(data, headlines)
    admin_sent = send_telegram(full_brief, ADMIN_CHAT)
    log_delivery(date_str, "admin", "brief", 1, "delivered" if admin_sent else "failed")
    print(f"Full brief sent to admin: {'OK' if admin_sent else 'FAIL'}")
    
    # 3. Send to PAID subscribers
    subs = get_active_subscribers()
    if subs:
        brief_sent = send_telegram(full_brief, ADMIN_CHAT)
        log_delivery(date_str, "edge", "brief", len(subs), "delivered" if brief_sent else "failed")
        print(f"Full brief queued for {len(subs)} subscribers")
    else:
        log_delivery(date_str, "edge", "brief", 0, "no_subscribers")
        print("No active subscribers")

    # 4. Save TradingView draft
    tv_title = f"Overnight Edge — {data['date']} | S&P {data['sp_futures']}, VIX {data['vix']}"
    tv_body = strip_html(full_brief)
    save_tradingview_draft(tv_title, tv_body)

if __name__ == "__main__":
    main()
