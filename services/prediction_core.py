import os
import csv
import json
import urllib.request
from datetime import datetime, timezone, timedelta
import time

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
        print(f"Telegram send failed: {e}")
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

def fetch_polymarket_data():
    """Fetch active markets from Polymarket"""
    try:
        url = "https://gamma-api.polymarket.com/markets?limit=20&active=true&closed=false"
        req = urllib.request.Request(url, headers={"User-Agent": "OvernightEdgeBot/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        markets = []
        for m in data.get("markets", [])[:10]:
            markets.append({
                "title": m.get("question", "Unknown"),
                "probability": m.get("probability", 0.5),
                "volume": m.get("volume", 0),
                "url": f"https://polymarket.com/event/{m.get('slug', '')}"
            })
        return markets
    except Exception as e:
        print(f"Polymarket fetch error: {e}")
        return []

def fetch_kalshi_data():
    """Fetch active markets from Kalshi"""
    try:
        url = "https://trading-api.kalshi.com/trade-api/v2/events?status=open&limit=10"
        req = urllib.request.Request(url, headers={"User-Agent": "OvernightEdgeBot/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        markets = []
        for e in data.get("events", [])[:10]:
            markets.append({
                "title": e.get("title", "Unknown"),
                "yes_price": e.get("yes_price", 50),
                "volume": e.get("volume", 0)
            })
        return markets
    except Exception as e:
        print(f"Kalshi fetch error: {e}")
        return []

def search_prediction_sentiment(query):
    """Search X/Twitter for prediction market sentiment"""
    try:
        import urllib.parse
        bearer = "AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3DhUBulTxX7eRF9rfTKDQcP6z0acMTEtkWv7NnIqZtI7zJxlIcxy"
        bearer = urllib.parse.unquote(bearer)
        url = f"https://api.twitter.com/2/tweets/search/recent?query={urllib.parse.quote(query)}&max_results=20"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}", "User-Agent": "OvernightEdgeBot/1.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        tweets = data.get("data", [])
        
        bullish = sum(1 for t in tweets if any(w in t.get("text", "").lower() for w in ["bullish", "up", "win", "yes", "long"]))
        bearish = sum(1 for t in tweets if any(w in t.get("text", "").lower() for w in ["bearish", "down", "lose", "no", "short"]))
        total = len(tweets)
        
        if total == 0:
            return 50, "neutral", 0
        
        sentiment = (bullish / total) * 100
        label = "bullish" if bullish > bearish else "bearish" if bearish > bullish else "neutral"
        return round(sentiment, 1), label, total
    except Exception as e:
        print(f"X sentiment error: {e}")
        return 50, "neutral", 0

def generate_prediction_report(session_name):
    """Generate PredictionCore report"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    polymarket = fetch_polymarket_data()
    kalshi = fetch_kalshi_data()
    
    events = []
    
    # Polymarket events
    for m in polymarket[:5]:
        prob = round(m["probability"] * 100, 1) if m["probability"] else 50
        x_sentiment, x_label, x_count = search_prediction_sentiment(m["title"])
        
        divergence = abs(prob - x_sentiment) > 10
        consensus = round((prob + x_sentiment) / 2, 1)
        
        momentum = "rising" if prob > 50 else "falling" if prob < 50 else "stable"
        
        events.append({
            "name": m["title"],
            "polymarket": prob,
            "kalshi": "N/A",
            "draftkings": "N/A",
            "x_sentiment": f"{x_sentiment}% ({x_label}, n={x_count})",
            "consensus": consensus,
            "divergence": divergence,
            "momentum": momentum
        })
        
        log_prediction(date_str, m["title"], "polymarket", f"{prob}%", "N/A", "N/A", f"{consensus}%", "YES" if divergence else "NO", f"X: {x_label}")
        time.sleep(1)
    
    # Kalshi events
    for k in kalshi[:3]:
        yes_price = k.get("yes_price", 50)
        prob = round(yes_price, 1)
        
        events.append({
            "name": k["title"],
            "polymarket": "N/A",
            "kalshi": f"{prob}%",
            "draftkings": "N/A",
            "x_sentiment": "N/A",
            "consensus": prob,
            "divergence": False,
            "momentum": "stable"
        })
        
        log_prediction(date_str, k["title"], "kalshi", "N/A", f"{prob}%", "N/A", f"{prob}%", "NO", "")
    
    # Build report
    event_lines = []
    for e in events:
        div_text = f"⚡ DIVERGENCE: Yes — Polymarket {e['polymarket']} vs X {e['x_sentiment']}" if e["divergence"] else "⚡ DIVERGENCE: No"
        event_lines.append(f"""📊 <b>{e['name']}</b>
Markets: Polymarket {e['polymarket']} | Kalshi {e['kalshi']} | DK {e['draftkings']} | X {e['x_sentiment']}
🎯 CONSENSUS: {e['consensus']}%
{div_text}
📈 MOMENTUM: {e['momentum']}""")
    
    arbitrage = [e for e in events if e["divergence"]]
    arb_text = "\n".join([f"• {e['name']}: spread detected" for e in arbitrage]) if arbitrage else "• No significant divergences"
    
    report = f"""🔮 <b>PREDICTIONCORE — {date_str} {session_name}</b>
━━━━━━━━━━━━━━━━━━━━

{"\n\n".join(event_lines)}

📊 <b>ARBITRAGE WATCH:</b>
{arb_text}

⚠️ INFORMATIONAL ONLY — NOT FINANCIAL ADVICE"""
    
    return report

def main():
    now = datetime.now(timezone.utc)
    hour = now.hour
    
    if 7 <= hour < 11:
        session = "MORNING SESSION"
    elif 11 <= hour < 15:
        session = "MIDDAY SESSION"
    elif 15 <= hour < 19:
        session = "AFTERNOON SESSION"
    else:
        session = "EVENING SESSION"
    
    print(f"Starting PredictionCore {session} at {now.strftime('%Y-%m-%d %H:%M')}")
    
    report = generate_prediction_report(session)
    
    # Send to admin
    send_telegram_photo(LOGO_PATH, report, ADMIN_CHAT)
    
    # Send to pulse-core and pulse-pro subscribers
    for tier in ["pulse-core", "pulse-pro"]:
        subs = get_subscribers(tier)
        for sub in subs:
            tg_id = sub.get("telegram_id", "")
            if tg_id:
                send_telegram(report, tg_id)
        print(f"PredictionCore {session} sent to {len(subs)} {tier} subscribers")
    
    print("PredictionCore complete")

if __name__ == "__main__":
    main()
