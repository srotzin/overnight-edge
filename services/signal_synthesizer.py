import os
import csv
import json
import urllib.request
from datetime import datetime, timezone

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

def log_signal(date_str, ticker, signal_type, score, s1, s2, s3, notes):
    with open("/mnt/user/overnight-edge/signal_accuracy.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, ticker, signal_type, score, s1, s2, s3, notes])

def log_delivery(date_str, tier, dtype, count, status):
    with open("/mnt/user/overnight-edge/delivery_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, tier, dtype, count, status])

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

def generate_public_teaser(ticker, signal_type, score, direction, detail):
    return f"""🚨 <b>SIGNAL DETECTED — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>TYPE:</b> {signal_type}
🎯 <b>CONFLUENCE:</b> {score}/5
📈 <b>DIRECTION:</b> {direction}
💰 <b>DETAIL:</b> {detail[:80]}...

Full signal + all sources + confluence analysis →
<a href="https://overnight-edge.onrender.com">overnight-edge.onrender.com</a>"""

def generate_full_alert(signal):
    return f"""🚨 <b>SIGNALSYNTHESIZER — {signal['ticker']}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>TYPE:</b> {signal['type']}
🎯 <b>CONFLUENCE:</b> {signal['score']}/5
📈 <b>DIRECTION:</b> {signal['direction']}
💰 <b>DETAIL:</b> {signal['detail']}
🔗 <b>SOURCES:</b> {', '.join(signal['sources'])}
⏰ <b>TIME:</b> {signal['time']}
⚠️ NOT FINANCIAL ADVICE"""

def generate_signals():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M")
    signals = []
    return signals

def main():
    signals = generate_signals()
    
    for signal in signals:
        # 1. ALWAYS post teaser to public channel (growth) with dark logo
        teaser = generate_public_teaser(
            signal['ticker'], signal['type'], signal['score'],
            signal['direction'], signal['detail']
        )
        public_sent = send_telegram_photo(LOGO_PATH, teaser, PUBLIC_CHANNEL)
        print(f"Public teaser for {signal['ticker']}: {'OK' if public_sent else 'FAIL'}")
        
        # 2. Full alert to admin (you) for review
        full = generate_full_alert(signal)
        send_telegram(full, ADMIN_CHAT)
        
        # 3. Full alert to PAID subscribers: signal, x10, x20, pulse-core, pulse-pro
        if signal.get("score", 0) >= 3:
            total_subs = 0
            for tier in ["signal", "x10", "x20", "pulse-core", "pulse-pro"]:
                subs = get_subscribers(tier)
                total_subs += len(subs)
                for sub in subs:
                    tg_id = sub.get("telegram_id", "")
                    if tg_id:
                        send_telegram(full, tg_id)
            
            log_signal(
                signal['time'], signal['ticker'], signal['type'],
                signal['score'], signal['sources'][0] if signal['sources'] else "",
                signal['sources'][1] if len(signal['sources']) > 1 else "",
                signal['sources'][2] if len(signal['sources']) > 2 else "",
                "delivered"
            )
            log_delivery(signal['time'], "signal", "alert", total_subs, "delivered")
            print(f"Full alert for {signal['ticker']}: OK ({total_subs} subscribers)")

if __name__ == "__main__":
    main()
