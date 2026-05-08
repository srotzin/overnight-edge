import os
import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import time

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
PUBLIC_CHANNEL = "-1003828989254"
ADMIN_CHAT = "5975342168"
LOGO_PATH = "/mnt/user/overnight-edge/cartoons/overnight_logo_dark.jpeg"

TWITTER_BEARER = urllib.parse.unquote("AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3DhUBulTxX7eRF9rfTKDQcP6z0acMTEtkWv7NnIqZtI7zJxlIcxy")

MONITORED_ACCOUNTS = [
    "CryptoCred", "IamNomad", "LightCrypto", "IncomeSharks", "PeterLBrandt",
    "CryptoKaleo", "woonomic", "RaoulGMI", "TheCryptoDog", "CryptoCapo_",
    "TraderMayne", "Trader_XO", "CryptoMichNL", "AltcoinPsycho", "MrMichaelNye",
    "CryptoWendyO", "Throne", "CryptoISO", "MooMsyndrome", "FintechFraming"
]

SIGNAL_KEYWORDS = [
    "perp", "perpetual", "futures", "option", "call", "put", "sweep", "flow",
    "gamma", "delta", "vega", "IV", "implied vol", "long", "short", "squeeze",
    "liquidation", "funding", "basis", "contango", "backwardation", "synthetic",
    "leveraged", "BTC", "ETH", "SOL", "NVDA", "TSLA", "SPY", "QQQ", "GLD", "USO", "EURUSD", "USDJPY"
]

TICKER_KEYWORDS = ["BTC", "ETH", "SOL", "NVDA", "TSLA", "SPY", "QQQ", "GLD", "USO", "EURUSD", "USDJPY"]

ASSET_MAP = {
    "perp": "perps", "perpetual": "perps", "futures": "derivatives",
    "option": "derivatives", "call": "derivatives", "put": "derivatives",
    "sweep": "derivatives", "flow": "derivatives", "gamma": "derivatives",
    "delta": "derivatives", "vega": "derivatives", "IV": "derivatives",
    "implied vol": "derivatives", "synthetic": "synthetics",
    "BTC": "crypto", "ETH": "crypto", "SOL": "crypto",
    "NVDA": "equities", "TSLA": "equities", "SPY": "equities", "QQQ": "equities",
    "GLD": "commodities", "USO": "commodities", "EURUSD": "fx", "USDJPY": "fx"
}

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

def log_xsignal(date_str, ticker, signal_type, score, accounts, asset_class, notes):
    with open("/mnt/user/overnight-edge/xsignal_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, ticker, signal_type, score, accounts, asset_class, notes])

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

def twitter_api_request(endpoint, params=None):
    url = f"https://api.twitter.com/2/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TWITTER_BEARER}", "User-Agent": "OvernightEdgeBot/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Twitter API error: {e}")
        return None

def get_user_id(username):
    data = twitter_api_request(f"users/by/username/{username}")
    if data and "data" in data:
        return data["data"]["id"]
    return None

def get_recent_tweets(user_id, max_results=5):
    params = {"max_results": max_results, "tweet.fields": "created_at,public_metrics", "exclude": "retweets,replies"}
    return twitter_api_request(f"users/{user_id}/tweets", params)

def search_recent_tweets(query, max_results=100):
    params = {"query": query, "max_results": max_results, "tweet.fields": "created_at,public_metrics,author_id", "expansions": "author_id", "user.fields": "username"}
    return twitter_api_request("tweets/search/recent", params)

def extract_signal_data(text):
    text_lower = text.lower()
    found_tickers = [t for t in TICKER_KEYWORDS if t.lower() in text_lower or f"${t.lower()}" in text_lower]
    found_keywords = [kw for kw in SIGNAL_KEYWORDS if kw.lower() in text_lower]
    
    bullish = ["long", "buy", "bull", "up", "squeeze", "calls", "pump"]
    bearish = ["short", "sell", "bear", "down", "dump", "puts", "liquidation"]
    bull_count = sum(1 for s in bullish if s in text_lower)
    bear_count = sum(1 for s in bearish if s in text_lower)
    
    if bull_count > bear_count:
        direction = "bullish"
    elif bear_count > bull_count:
        direction = "bearish"
    else:
        direction = "neutral"
    
    return {"tickers": found_tickers, "keywords": found_keywords, "direction": direction}

def determine_asset_class(keywords, tickers):
    classes = set()
    for kw in keywords:
        if kw in ASSET_MAP:
            classes.add(ASSET_MAP[kw])
    for t in tickers:
        if t in ASSET_MAP:
            classes.add(ASSET_MAP[t])
    return "/".join(sorted(classes)) if classes else "mixed"

def calculate_confluence_score(mentions):
    num_accounts = len(set(m["account"] for m in mentions))
    all_keywords = set()
    for m in mentions:
        all_keywords.update(m["keywords"])
    
    if num_accounts >= 5:
        score = 5
    elif num_accounts == 4:
        score = 4
    elif num_accounts == 3:
        score = 3
    elif num_accounts == 2:
        score = 2
    else:
        score = 1
    
    if len(all_keywords) >= 4:
        score = min(5, score + 1)
    
    return score

def check_cross_asset(mentions):
    """Check if same ticker appears across multiple asset classes"""
    classes = set()
    for m in mentions:
        for kw in m["keywords"]:
            if kw in ASSET_MAP:
                classes.add(ASSET_MAP[kw])
    return len(classes) >= 2

def generate_x20_instant_alert(ticker, score, mentions, asset_class, direction, cross_asset, velocity):
    accounts = list(set(m["account"] for m in mentions))[:7]
    account_list = ", ".join([f"@{a}" for a in accounts])
    
    keywords = set()
    for m in mentions:
        keywords.update(m["keywords"])
    kw_list = ", ".join(sorted(keywords)[:6])
    
    cross_text = "🔄 CROSS-ASSET CONFIRMED" if cross_asset else ""
    
    alert = f"""🔥 <b>X20 SIGNAL — {ticker} — HIGH CONFLUENCE</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>ACCOUNTS:</b> {account_list}
📊 <b>ASSET CLASS:</b> {asset_class}
🎯 <b>CONFLUENCE:</b> {score}/5 {cross_text}
📈 <b>DIRECTION:</b> {direction}
💰 <b>SYNTHESIS:</b> High-confluence signal detected across {len(accounts)} monitored accounts. Key themes: {kw_list}. Aggregated positioning suggests {direction} momentum building across {asset_class}.
📊 <b>CROSS-ASSET:</b> {"Yes — confirmed across multiple asset classes" if cross_asset else "Single asset class"}
🔗 <b>SOURCES:</b> Monitored X accounts (aggregated intelligence)
⏰ <b>VELOCITY:</b> {velocity} posts in last hour
⚠️ NOT FINANCIAL ADVICE"""
    
    return alert

def generate_x20_standard_alert(ticker, score, mentions, asset_class, direction):
    accounts = list(set(m["account"] for m in mentions))[:5]
    account_list = ", ".join([f"@{a}" for a in accounts])
    
    keywords = set()
    for m in mentions:
        keywords.update(m["keywords"])
    kw_list = ", ".join(sorted(keywords)[:5])
    
    alert = f"""📡 <b>X20 SIGNAL — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>ACCOUNTS:</b> {account_list}
📊 <b>ASSET CLASS:</b> {asset_class}
🎯 <b>CONFLUENCE:</b> {score}/5
📈 <b>DIRECTION:</b> {direction}
💰 <b>KEY SIGNALS:</b> {len(accounts)} accounts converging on {ticker}. Key themes: {kw_list}. Aggregated positioning suggests {direction} momentum.
🔗 <b>SOURCES:</b> Monitored X accounts (aggregated intelligence)
⚠️ NOT FINANCIAL ADVICE"""
    
    return alert

def check_monitored_accounts():
    all_mentions = {}
    for username in MONITORED_ACCOUNTS:
        print(f"Checking @{username}...")
        user_id = get_user_id(username)
        if not user_id:
            continue
        tweets_data = get_recent_tweets(user_id, max_results=5)
        if not tweets_data or "data" not in tweets_data:
            continue
        
        for tweet in tweets_data.get("data", []):
            tweet_text = tweet.get("text", "")
            created_at = tweet.get("created_at", "")
            try:
                tweet_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) - tweet_time > timedelta(hours=2):
                    continue
            except:
                continue
            
            signal_data = extract_signal_data(tweet_text)
            if signal_data["tickers"] and signal_data["keywords"]:
                for ticker in signal_data["tickers"]:
                    if ticker not in all_mentions:
                        all_mentions[ticker] = []
                    all_mentions[ticker].append({
                        "account": username,
                        "keywords": signal_data["keywords"],
                        "direction": signal_data["direction"],
                        "time": created_at
                    })
        time.sleep(1)
    return all_mentions

def broader_x_search():
    """Search all of X for trending trading keywords"""
    query = " OR ".join([f"{kw}" for kw in ["perp", "futures", "options flow", "squeeze", "liquidation"]])
    results = search_recent_tweets(query, max_results=50)
    if not results or "data" not in results:
        return {}
    
    # Extract tickers and build mentions
    mentions = {}
    for tweet in results.get("data", []):
        text = tweet.get("text", "")
        signal_data = extract_signal_data(text)
        if signal_data["tickers"]:
            for ticker in signal_data["tickers"]:
                if ticker not in mentions:
                    mentions[ticker] = []
                mentions[ticker].append({
                    "account": "broader_x",
                    "keywords": signal_data["keywords"],
                    "direction": signal_data["direction"],
                    "time": tweet.get("created_at", "")
                })
    return mentions

def send_eod_synthesis():
    """Generate and send end-of-day synthesis to x20 and pulse-pro subscribers"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Read today's log
    tickers_mentioned = {}
    directions = {"bullish": 0, "bearish": 0, "neutral": 0}
    
    try:
        with open("/mnt/user/overnight-edge/xsignal_log.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("date", "").startswith(date_str):
                    ticker = row.get("ticker", "")
                    direction = row.get("notes", "").replace("Direction: ", "")
                    if ticker:
                        tickers_mentioned[ticker] = tickers_mentioned.get(ticker, 0) + 1
                    if "bullish" in direction:
                        directions["bullish"] += 1
                    elif "bearish" in direction:
                        directions["bearish"] += 1
                    else:
                        directions["neutral"] += 1
    except:
        pass
    
    top_tickers = sorted(tickers_mentioned.items(), key=lambda x: x[1], reverse=True)[:5]
    top_text = "\n".join([f"• {t}: {count} alerts" for t, count in top_tickers]) if top_tickers else "• No significant signals today"
    
    total = sum(directions.values())
    if total > 0:
        bias = f"Bullish: {directions['bullish']} | Bearish: {directions['bearish']} | Neutral: {directions['neutral']}"
    else:
        bias = "No directional signals captured today"
    
    report = f"""📊 <b>X20 EOD SYNTHESIS — {date_str}</b>
━━━━━━━━━━━━━━━━━━━━
<b>Most-Mentioned Tickers:</b>
{top_text}

<b>Directional Bias:</b>
{bias}

<b>Cross-Asset Winners:</b>
• Review individual alerts for cross-asset tagged signals

<b>Sentiment Shift:</b>
• Aggregated monitoring complete. See individual alerts for specifics.

⚠️ NOT FINANCIAL ADVICE — INFORMATIONAL ONLY"""
    
    # Send to admin
    send_telegram_photo(LOGO_PATH, report, ADMIN_CHAT)
    
    # Send to x20 and pulse-pro subscribers
    for tier in ["x20", "pulse-pro"]:
        subs = get_subscribers(tier)
        for sub in subs:
            tg_id = sub.get("telegram_id", "")
            if tg_id:
                send_telegram(report, tg_id)
    
    print("EOD synthesis sent")

def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M")
    print(f"Starting X20 Pro scan at {date_str}")
    
    # Check if EOD time (4:30 PM EST = 21:30 UTC)
    if now.hour == 21 and now.minute < 20:
        print("EOD synthesis time detected")
        send_eod_synthesis()
        return
    
    # 1. Check monitored accounts
    mentions = check_monitored_accounts()
    
    # 2. Broader X search (Pro feature)
    broader = broader_x_search()
    
    # Merge broader into mentions
    for ticker, b_mentions in broader.items():
        if ticker in mentions:
            mentions[ticker].extend(b_mentions)
        else:
            mentions[ticker] = b_mentions
    
    alerts_sent = 0
    for ticker, ticker_mentions in mentions.items():
        score = calculate_confluence_score(ticker_mentions)
        
        if score >= 3:
            directions = [m["direction"] for m in ticker_mentions]
            direction = max(set(directions), key=directions.count)
            
            asset_class = determine_asset_class(
                [kw for m in ticker_mentions for kw in m["keywords"]],
                [ticker]
            )
            
            cross_asset = check_cross_asset(ticker_mentions)
            if cross_asset and score < 5:
                score = min(5, score + 1)
            
            velocity = len([m for m in ticker_mentions if m.get("account") != "broader_x"])
            
            # Score 4+ = instant high-confluence format
            if score >= 4:
                alert_text = generate_x20_instant_alert(ticker, score, ticker_mentions, asset_class, direction, cross_asset, velocity)
            else:
                alert_text = generate_x20_standard_alert(ticker, score, ticker_mentions, asset_class, direction)
            
            # Public teaser
            teaser = f"""🔥 <b>X20 SIGNAL — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>CONFLUENCE:</b> {score}/5
📈 <b>DIRECTION:</b> {direction}
💰 <b>MONITORED:</b> {len(set(m['account'] for m in ticker_mentions))} accounts

Full analysis + all tiers →
<a href="https://overnight-edge.onrender.com">overnight-edge.onrender.com</a>"""
            
            send_telegram_photo(LOGO_PATH, teaser, PUBLIC_CHANNEL)
            time.sleep(2)
            
            # Full alert to admin
            send_telegram_photo(LOGO_PATH, alert_text, ADMIN_CHAT)
            
            # Send to x20 and pulse-pro subscribers
            for tier in ["x20", "pulse-pro"]:
                subs = get_subscribers(tier)
                for sub in subs:
                    tg_id = sub.get("telegram_id", "")
                    if tg_id:
                        send_telegram(alert_text, tg_id)
            
            log_xsignal(date_str, ticker, "x20", score,
                       ", ".join(set(m["account"] for m in ticker_mentions)),
                       asset_class, f"Direction: {direction}, CrossAsset: {cross_asset}")
            
            alerts_sent += 1
            print(f"X20 alert sent for {ticker}: score {score}")
        
        time.sleep(2)
    
    print(f"X20 scan complete. {alerts_sent} alerts sent.")

if __name__ == "__main__":
    main()
