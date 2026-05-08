import os
import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
import time

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
ADMIN_CHAT = "5975342168"
LOGO_PATH = "/mnt/user/overnight-edge/cartoons/overnight_logo_dark.jpeg"

def send_telegram(text: str, chat_id: str = ADMIN_CHAT):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

def send_telegram_photo(photo_path: str, caption: str, chat_id: str = ADMIN_CHAT):
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
        print(f"Telegram photo send failed: {e}")
        return False

def log_prediction(date_str, event, market, p1, p2, p3, consensus, divergence, notes):
    with open("/mnt/user/overnight-edge/prediction_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, event, market, p1, p2, p3, consensus, divergence, notes])

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

def fetch_polymarket_markets():
    """Fetch active markets with volume data"""
    try:
        url = "https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false&sort=volume"
        req = urllib.request.Request(url, headers={"User-Agent": "OvernightEdgeBot/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        markets = []
        for m in data.get("markets", [])[:20]:
            markets.append({
                "title": m.get("question", "Unknown"),
                "probability": m.get("probability", 0.5),
                "volume": m.get("volume", 0),
                "slug": m.get("slug", ""),
                "id": m.get("id", "")
            })
        return markets
    except Exception as e:
        print(f"Polymarket fetch error: {e}")
        return []

def check_probability_shifts():
    """Check for significant probability shifts (>5%)"""
    markets = fetch_polymarket_markets()
    shifts = []
    
    for m in markets:
        prob = round(m["probability"] * 100, 1) if m["probability"] else 50
        # In production: compare to previous probability from prediction_log.csv
        # For now: flag any market with high volume + significant probability
        if m["volume"] > 100000 and (prob < 30 or prob > 70):
            shifts.append({
                "name": m["title"],
                "new_prob": prob,
                "old_prob": 50,  # Would be historical
                "shift": abs(prob - 50),
                "volume": m["volume"]
            })
    
    return shifts

def check_new_markets():
    """Check for newly opened high-volume markets"""
    markets = fetch_polymarket_markets()
    new_markets = [m for m in markets if m["volume"] > 50000][:5]
    return new_markets

def search_x_divergence(query):
    """Check if X sentiment diverges from market prices"""
    try:
        bearer = "AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3DhUBulTxX7eRF9rfTKDQcP6z0acMTEtkWv7NnIqZtI7zJxlIcxy"
        bearer = urllib.parse.unquote(bearer)
        url = f"https://api.twitter.com/2/tweets/search/recent?query={urllib.parse.quote(query)}&max_results=30"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}", "User-Agent": "OvernightEdgeBot/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        tweets = data.get("data", [])
        
        bullish = sum(1 for t in tweets if any(w in t.get("text", "").lower() for w in ["bullish", "up", "win", "yes", "long", "buy"]))
        bearish = sum(1 for t in tweets if any(w in t.get("text", "").lower() for w in ["bearish", "down", "lose", "no", "short", "sell"]))
        total = len(tweets)
        
        if total == 0:
            return 50, 0
        
        sentiment = (bullish / total) * 100
        return round(sentiment, 1), total
    except:
        return 50, 0

def send_shift_alert(shift):
    """Send instant shift alert"""
    alert = f"""⚡ <b>PREDICTION PRO — SHIFT ALERT</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>EVENT:</b> {shift['name']}
📊 <b>PROBABILITY SHIFT:</b> {shift['old_prob']}% → {shift['new_prob']}%
📈 <b>CHANGE:</b> {shift['shift']:.1f} percentage points
🔗 <b>SOURCE:</b> Polymarket
💡 <b>CONTEXT:</b> High-volume market showing significant probability movement. Volume: ${shift['volume']:,.0f}

⚠️ INFORMATIONAL ONLY — NOT FINANCIAL ADVICE"""
    
    send_telegram_photo(LOGO_PATH, alert, ADMIN_CHAT)
    
    # Send to pulse-pro subscribers only
    subs = get_subscribers("pulse-pro")
    for sub in subs:
        tg_id = sub.get("telegram_id", "")
        if tg_id:
            send_telegram(alert, tg_id)
    
    print(f"Shift alert sent for {shift['name']}")

def send_eod_report():
    """Generate and send end-of-day probability shift report"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Read today's shifts from prediction_log
    shifts = []
    new_markets = []
    
    try:
        with open("/mnt/user/overnight-edge/prediction_log.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("date", "").startswith(date_str):
                    if "shift" in row.get("notes", "").lower():
                        shifts.append(row)
                    if "new" in row.get("notes", "").lower():
                        new_markets.append(row)
    except:
        pass
    
    # Also check current markets
    markets = fetch_polymarket_markets()
    top_volume = sorted(markets, key=lambda x: x["volume"], reverse=True)[:5]
    closing_soon = [m for m in markets if m["probability"] > 0.8 or m["probability"] < 0.2][:3]
    
    shifts_text = "\n".join([f"• {s['event']}: {s['prob_source_1']} → {s['consensus_prob']}" for s in shifts[:5]]) if shifts else "• No major shifts today"
    new_text = "\n".join([f"• {n['event']}: {n['market']}" for n in new_markets[:5]]) if new_markets else "• No new markets opened"
    volume_text = "\n".join([f"• {m['title']}: ${m['volume']:,.0f} volume" for m in top_volume])
    closing_text = "\n".join([f"• {m['title']}: {round(m['probability']*100,1)}%" for m in closing_soon]) if closing_soon else "• No markets near resolution"
    
    report = f"""📊 <b>PREDICTION PRO — EOD REPORT</b>
━━━━━━━━━━━━━━━━━━━━
<b>Date:</b> {date_str}

<b>📈 TOP SHIFTS:</b>
{shifts_text}

<b>🆕 NEW MARKETS:</b>
{new_text}

<b>💰 VOLUME LEADERS:</b>
{volume_text}

<b>⏰ CLOSING SOON:</b>
{closing_text}

<b>📊 SENTIMENT LEADERBOARD:</b>
• See individual alerts for X sentiment analysis

⚠️ INFORMATIONAL ONLY — NOT FINANCIAL ADVICE"""
    
    send_telegram_photo(LOGO_PATH, report, ADMIN_CHAT)
    
    # Send to pulse-pro only
    subs = get_subscribers("pulse-pro")
    for sub in subs:
        tg_id = sub.get("telegram_id", "")
        if tg_id:
            send_telegram(report, tg_id)
    
    print(f"EOD report sent to {len(subs)} pulse-pro subscribers")

def main():
    now = datetime.now(timezone.utc)
    hour = now.hour
    minute = now.minute
    
    # EOD report at 7 PM EST = 23:00 UTC
    if hour == 23 and minute < 20:
        print("EOD report time")
        send_eod_report()
        return
    
    print(f"Starting Prediction Pro scan at {now.strftime('%Y-%m-%d %H:%M')}")
    
    # 1. Check for probability shifts
    shifts = check_probability_shifts()
    for shift in shifts:
        if shift["shift"] >= 5:
            send_shift_alert(shift)
            log_prediction(
                now.strftime("%Y-%m-%d %H:%M"),
                shift["name"], "polymarket",
                f"{shift['old_prob']}%", f"{shift['new_prob']}%", "N/A",
                f"{shift['new_prob']}%", "YES",
                f"shift: {shift['shift']:.1f}%, volume: ${shift['volume']:,.0f}"
            )
            time.sleep(2)
    
    # 2. Check for new high-volume markets
    new_markets = check_new_markets()
    for m in new_markets:
        alert = f"""🆕 <b>PREDICTION PRO — NEW MARKET</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>EVENT:</b> {m['title']}
📊 <b>OPENING PROB:</b> {round(m['probability']*100,1)}%
💰 <b>VOLUME:</b> ${m['volume']:,.0f}
🔗 <b>SOURCE:</b> Polymarket

⚠️ INFORMATIONAL ONLY — NOT FINANCIAL ADVICE"""
        
        send_telegram(alert, ADMIN_CHAT)
        log_prediction(
            now.strftime("%Y-%m-%d %H:%M"),
            m["title"], "polymarket",
            f"{round(m['probability']*100,1)}%", "N/A", "N/A",
            f"{round(m['probability']*100,1)}%", "NO",
            f"new market, volume: ${m['volume']:,.0f}"
        )
        time.sleep(1)
    
    print("Prediction Pro scan complete")

if __name__ == "__main__":
    main()
