#!/usr/bin/env python3
"""XSignal Basic — Twitter/X Account Monitor + Confluence Synthesizer"""

import os
import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import time
import re

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
PUBLIC_CHANNEL = "-1003828989254"
ADMIN_CHAT = "5975342168"

LOGO_PATH = "/mnt/user/overnight-edge/cartoons/overnight_logo_dark.jpeg"

# Twitter API v2 Bearer Token
TWITTER_BEARER = "AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3DhUBulTxX7eRF9rfTKDQcP6z0acMTEtkWv7NnIqZtI7zJxlIcxy"

# Monitored accounts (20)
MONITORED_ACCOUNTS = [
    "CryptoCred", "IamNomad", "LightCrypto", "IncomeSharks", "PeterLBrandt",
    "CryptoKaleo", "woonomic", "RaoulGMI", "TheCryptoDog", "CryptoCapo_",
    "TraderMayne", "Trader_XO", "CryptoMichNL", "AltcoinPsycho", "MrMichaelNye",
    "CryptoWendyO", "Throne", "CryptoISO", "MooMsyndrome", "FintechFraming"
]

# Signal keywords
SIGNAL_KEYWORDS = [
    "perp", "perpetual", "futures", "option", "call", "put", "sweep", "flow",
    "gamma", "delta", "vega", "IV", "implied vol", "long", "short", "squeeze",
    "liquidation", "funding", "basis", "contango", "backwardation", "synthetic",
    "sUSD", "mirror", "leveraged", "BTC", "ETH", "SOL", "NVDA", "TSLA",
    "SPY", "QQQ", "GLD", "USO", "EURUSD", "USDJPY"
]

# Asset class mapping
ASSET_MAP = {
    "perp": "perps", "perpetual": "perps", "futures": "derivatives",
    "option": "derivatives", "call": "derivatives", "put": "derivatives",
    "sweep": "derivatives", "flow": "derivatives", "gamma": "derivatives",
    "delta": "derivatives", "vega": "derivatives", "IV": "derivatives",
    "implied vol": "derivatives", "synthetic": "synthetics", "sUSD": "synthetics",
    "mirror": "synthetics", "BTC": "crypto", "ETH": "crypto", "SOL": "crypto",
    "NVDA": "equities", "TSLA": "equities", "SPY": "equities", "QQQ": "equities",
    "GLD": "commodities", "USO": "commodities", "EURUSD": "fx", "USDJPY": "fx"
}

TICKER_KEYWORDS = ["BTC", "ETH", "SOL", "NVDA", "TSLA", "SPY", "QQQ", "GLD", "USO", "EURUSD", "USDJPY"]

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

def get_xsignal_subscribers(tier_filter=None):
    subs = []
    try:
        with open("/mnt/user/overnight-edge/xsignal_subscribers.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("status") == "active":
                    if tier_filter is None or row.get("tier") == tier_filter:
                        subs.append(row)
    except Exception as e:
        print(f"Subscriber read error: {e}")
    return subs

def twitter_api_request(endpoint, params=None):
    """Make authenticated Twitter API v2 request"""
    url = f"https://api.twitter.com/2/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TWITTER_BEARER}",
        "User-Agent": "OvernightEdgeBot/1.0"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Twitter API error: {e}")
        return None

def get_user_id(username):
    """Resolve username to Twitter user ID"""
    data = twitter_api_request(f"users/by/username/{username}")
    if data and "data" in data:
        return data["data"]["id"]
    return None

def get_recent_tweets(user_id, max_results=10):
    """Fetch recent tweets from a user"""
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,context_annotations",
        "exclude": "retweets,replies"
    }
    return twitter_api_request(f"users/{user_id}/tweets", params)

def search_recent_tweets(query, max_results=100):
    """Search recent tweets matching query"""
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,author_id",
        "expansions": "author_id",
        "user.fields": "username"
    }
    return twitter_api_request("tweets/search/recent", params)

def extract_signal_data(tweet_text):
    """Extract ticker, direction, keywords from tweet text"""
    text_lower = tweet_text.lower()
    
    # Find tickers
    found_tickers = []
    for ticker in TICKER_KEYWORDS:
        if ticker.lower() in text_lower or f"${ticker.lower()}" in text_lower:
            found_tickers.append(ticker)
    
    # Find keywords
    found_keywords = []
    for kw in SIGNAL_KEYWORDS:
        if kw.lower() in text_lower:
            found_keywords.append(kw)
    
    # Determine direction
    bullish_signals = ["long", "buy", "bull", "up", "squeeze", "calls", "pump"]
    bearish_signals = ["short", "sell", "bear", "down", "dump", "puts", "liquidation"]
    
    bull_count = sum(1 for s in bullish_signals if s in text_lower)
    bear_count = sum(1 for s in bearish_signals if s in text_lower)
    
    if bull_count > bear_count:
        direction = "bullish"
    elif bear_count > bull_count:
        direction = "bearish"
    else:
        direction = "neutral"
    
    return {
        "tickers": found_tickers,
        "keywords": found_keywords,
        "direction": direction,
        "raw_text": tweet_text
    }

def determine_asset_class(keywords, tickers):
    """Map keywords/tickers to asset class"""
    classes = set()
    for kw in keywords:
        if kw in ASSET_MAP:
            classes.add(ASSET_MAP[kw])
    for t in tickers:
        if t in ASSET_MAP:
            classes.add(ASSET_MAP[t])
    if not classes:
        return "mixed"
    return "/".join(sorted(classes))

def synthesize_signal(ticker, mentions, direction):
    """Generate synthesized signal text (NOT verbatim tweets)"""
    accounts = [m["account"] for m in mentions]
    keywords = set()
    for m in mentions:
        keywords.update(m["keywords"])
    
    # Build synthesis in our own words
    kw_list = ", ".join(sorted(keywords)[:5])
    account_list = ", ".join([f"@{a}" for a in accounts[:5]])
    
    direction_emoji = "📈" if direction == "bullish" else "📉" if direction == "bearish" else "➡️"
    
    synthesis = f"{direction_emoji} Multiple monitored accounts showing {direction} positioning in {ticker}. Key themes: {kw_list}. Convergence detected across {len(accounts)} sources within monitoring window."
    
    return synthesis, account_list

def generate_xsignal_alert(ticker, score, mentions, asset_class, direction):
    """Generate XSignal alert with dark logo"""
    synthesis, account_list = synthesize_signal(ticker, mentions, direction)
    
    return f"""📡 <b>XSIGNAL — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>ACCOUNTS:</b> {account_list}
📊 <b>ASSET CLASS:</b> {asset_class}
🎯 <b>CONFLUENCE:</b> {score}/5
📈 <b>DIRECTION:</b> {direction}
💰 <b>KEY SIGNALS:</b> {synthesis}
🔗 <b>SOURCES:</b> Monitored X accounts (aggregated intelligence)
⚠️ NOT FINANCIAL ADVICE"""

def check_monitored_accounts():
    """Check all 20 monitored accounts for signal keywords"""
    all_mentions = {}  # ticker -> list of mentions
    
    for username in MONITORED_ACCOUNTS:
        print(f"Checking @{username}...")
        user_id = get_user_id(username)
        if not user_id:
            print(f"  Could not resolve @{username}")
            continue
        
        tweets_data = get_recent_tweets(user_id, max_results=5)
        if not tweets_data or "data" not in tweets_data:
            print(f"  No tweets from @{username}")
            continue
        
        for tweet in tweets_data.get("data", []):
            tweet_text = tweet.get("text", "")
            created_at = tweet.get("created_at", "")
            
            # Only check tweets from last 2 hours
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
        
        time.sleep(1)  # Rate limit respect
    
    return all_mentions

def calculate_confluence_score(mentions):
    """Score based on account count + keyword diversity"""
    num_accounts = len(set(m["account"] for m in mentions))
    all_keywords = set()
    for m in mentions:
        all_keywords.update(m["keywords"])
    
    # Base score from account count
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
    
    # Boost for keyword diversity
    if len(all_keywords) >= 4:
        score = min(5, score + 1)
    
    return score

def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M")
    print(f"Starting XSignal Basic scan at {date_str}")
    
    mentions = check_monitored_accounts()
    
    alerts_sent = 0
    for ticker, ticker_mentions in mentions.items():
        score = calculate_confluence_score(ticker_mentions)
        
        if score >= 3:
            # Determine dominant direction
            directions = [m["direction"] for m in ticker_mentions]
            direction = max(set(directions), key=directions.count)
            
            asset_class = determine_asset_class(
                [kw for m in ticker_mentions for kw in m["keywords"]],
                [ticker]
            )
            
            alert_text = generate_xsignal_alert(ticker, score, ticker_mentions, asset_class, direction)
            
            # Send to public channel (teaser)
            public_teaser = f"""📡 <b>XSIGNAL — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>CONFLUENCE:</b> {score}/5
📈 <b>DIRECTION:</b> {direction}
💰 <b>MONITORED:</b> {len(set(m['account'] for m in ticker_mentions))} accounts

Full analysis + all tiers →
<a href="https://overnight-edge.onrender.com">overnight-edge.onrender.com</a>"""
            
            send_telegram_photo(LOGO_PATH, public_teaser, PUBLIC_CHANNEL)
            time.sleep(2)
            
            # Send full alert to admin
            send_telegram_photo(LOGO_PATH, alert_text, ADMIN_CHAT)
            
            # Send to subscribers
            subs = get_xsignal_subscribers()
            if subs:
                for sub in subs:
                    # In production: send to each subscriber's telegram_id
                    pass
            
            log_xsignal(date_str, ticker, "xsignal", score, 
                       ", ".join(set(m["account"] for m in ticker_mentions)),
                       asset_class, f"Direction: {direction}")
            
            alerts_sent += 1
            print(f"Alert sent for {ticker}: score {score}")
        
        time.sleep(2)
    
    print(f"Scan complete. {alerts_sent} alerts sent.")

if __name__ == "__main__":
    main()
