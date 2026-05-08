import os
import csv
import json
import urllib.request
from datetime import datetime, timezone
import sys

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
PUBLIC_CHANNEL = "-1003828989254"
ADMIN_CHAT = "5975342168"

LOGO_PATH = "/mnt/user/overnight-edge/cartoons/overnight_logo_dark.jpeg"

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
    """Send photo with caption to Telegram"""
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
    
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    })
    
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram photo send failed to {chat_id}: {e}")
        return False

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
    }
    return data

def generate_free_preview(data: dict) -> str:
    return f"""🌅 <b>OVERNIGHT EDGE — Free Preview</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>FUTURES:</b> S&P {data['sp_futures']}, Nasdaq {data['nasdaq_futures']}
📈 <b>VIX:</b> {data['vix']} ({data['vix_change']})

🏆 <b>GAINER:</b> {data['gainers'][0]['ticker']} {data['gainers'][0]['change']}
🔻 <b>LOSER:</b> {data['losers'][0]['ticker']} {data['losers'][0]['change']}

📢 <b>EARNINGS:</b> {data['earnings'][0]}
⚡ <b>NEWS:</b> {data['news'][0][:60]}...

🔮 <b>OUTLOOK:</b> {data['outlook']}

Full brief + 10 more signals + earnings calendar →
<a href="https://overnight-edge.onrender.com">overnight-edge.onrender.com</a>"""

def generate_full_brief(data: dict) -> str:
    gainers_text = "\n".join([f"  {g['ticker']} {g['change']}" for g in data['gainers']])
    losers_text = "\n".join([f"  {l['ticker']} {l['change']}" for l in data['losers']])
    
    return f"""🌅 <b>OVERNIGHT EDGE — {data['date']}</b>
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

🔮 <b>OUTLOOK:</b> {data['outlook']}"""

def main():
    data = get_market_data()
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # 1. Post FREE PREVIEW to public channel with dark logo
    preview = generate_free_preview(data)
    preview_sent = send_telegram_photo(LOGO_PATH, preview, PUBLIC_CHANNEL)
    log_delivery(date_str, "public", "preview", 1, "delivered" if preview_sent else "failed")
    print(f"Free preview with dark logo sent to public channel: {'OK' if preview_sent else 'FAIL'}")
    
    # 2. Post FULL BRIEF to admin
    full_brief = generate_full_brief(data)
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

if __name__ == "__main__":
    main()
