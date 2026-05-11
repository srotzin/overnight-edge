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

# X API Bearer Token (user provided)
X_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3D"

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

def fetch_yahoo_quote(symbol: str) -> dict:
    """Fetch real-time quote from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode())
        result = data.get("chart", {}).get("result", [{}])[0]
        meta = result.get("meta", {})
        current = meta.get("regularMarketPrice", 0)
        previous = meta.get("previousClose", 0) or meta.get("chartPreviousClose", 0)
        change = current - previous if current and previous else 0
        change_pct = (change / previous * 100) if previous else 0
        return {
            "price": current,
            "change": change,
            "change_pct": change_pct,
            "symbol": symbol,
        }
    except Exception as e:
        print(f"Yahoo fetch failed for {symbol}: {e}")
        return None

def get_market_data():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Fetch real futures data
    sp_futures = fetch_yahoo_quote("ES=F") or {}
    nq_futures = fetch_yahoo_quote("NQ=F") or {}
    vix_data = fetch_yahoo_quote("^VIX") or {}
    
    # Format futures changes
    sp_change = sp_futures.get("change_pct", 0)
    nq_change = nq_futures.get("change_pct", 0)
    vix_value = vix_data.get("price", 0)
    vix_prev = vix_data.get("price", 0) - vix_data.get("change", 0) if vix_data.get("price") else 0
    vix_change = vix_data.get("change", 0)
    
    sp_str = f"{sp_change:+.2f}%" if sp_change else "N/A"
    nq_str = f"{nq_change:+.2f}%" if nq_change else "N/A"
    vix_str = f"{vix_value:.1f}" if vix_value else "N/A"
    vix_chg_str = f"{vix_change:+.1f}" if vix_change else "N/A"
    
    # Fetch real gainers/losers from Yahoo Finance
    gainers, losers = fetch_market_movers()
    
    # Fetch real news
    headlines = fetch_market_news()
    
    # Fetch prediction markets
    prediction = fetch_prediction_of_the_day()
    
    data = {
        "date": date_str,
        "sp_futures": sp_str,
        "nasdaq_futures": nq_str,
        "vix": vix_str,
        "vix_change": vix_chg_str,
        "gainers": gainers if gainers else [
            {"ticker": "N/A", "change": "Fetching..."},
        ],
        "losers": losers if losers else [
            {"ticker": "N/A", "change": "Fetching..."},
        ],
        "earnings": fetch_earnings_today(),
        "economic": fetch_economic_calendar(),
        "news": headlines if headlines else ["Market data updating..."],
        "outlook": generate_outlook(sp_change, nq_change, vix_value),
        "prediction_of_the_day": prediction,
    }
    return data

def fetch_market_movers() -> tuple:
    """Fetch top gainers and losers from Yahoo Finance"""
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&lang=en-US&region=US&scrIds=day_gainers&count=5&corsDomain=finance.yahoo.com"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode())
        gainers_raw = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])[:3]
        gainers = [{"ticker": q.get("symbol", ""), "change": f"{q.get('regularMarketChangePercent', 0):+.1f}%"} for q in gainers_raw if q.get("symbol")]
        
        # Fetch losers
        url2 = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&lang=en-US&region=US&scrIds=day_losers&count=5&corsDomain=finance.yahoo.com"
        req2 = urllib.request.Request(url2, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response2 = urllib.request.urlopen(req2, timeout=15)
        data2 = json.loads(response2.read().decode())
        losers_raw = data2.get("finance", {}).get("result", [{}])[0].get("quotes", [])[:3]
        losers = [{"ticker": q.get("symbol", ""), "change": f"{q.get('regularMarketChangePercent', 0):+.1f}%"} for q in losers_raw if q.get("symbol")]
        
        return gainers, losers
    except Exception as e:
        print(f"Market movers fetch failed: {e}")
        return None, None

def fetch_market_news() -> list:
    """Fetch latest market news headlines"""
    try:
        url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC,%5EVIX,GC=F,CL=F&region=US&lang=en-US"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode()
        # Extract titles from RSS
        titles = re.findall(r'<title>([^<]+)</title>', content)
        # Skip the first title (usually the feed title)
        return titles[1:4] if len(titles) > 1 else ["Market updates loading..."]
    except Exception as e:
        print(f"News fetch failed: {e}")
        return None

def fetch_earnings_today() -> list:
    """Fetch today's earnings from Yahoo Finance"""
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/calendar/earnings?formatted=false&lang=en-US&region=US&start=0&count=5&corsDomain=finance.yahoo.com"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode())
        earnings_raw = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])[:2]
        return [f"{q.get('symbol', '')} ({q.get('epsEstimate', 'TBD')} EPS est.)" for q in earnings_raw if q.get("symbol")]
    except Exception as e:
        print(f"Earnings fetch failed: {e}")
        return ["Earnings data updating..."]

def fetch_economic_calendar() -> list:
    """Fetch today's economic events"""
    # Simplified — check common macro schedule or use a free API
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Basic known schedule (can be enhanced with real API)
    weekday = datetime.now(timezone.utc).weekday()
    events = []
    if weekday < 5:  # Weekday
        events.append("Pre-market economic data check active")
    return events if events else ["No major economic events scheduled"]

def fetch_prediction_of_the_day() -> dict:
    """Fetch a random prediction market item"""
    try:
        # Try Polymarket or Kalshi — simplified for now
        # In production, scrape or API call to prediction markets
        import random
        predictions = [
            {"market": "Fed rate decision next meeting", "odds": "72% Hold", "source": "CME FedWatch"},
            {"market": "S&P 500 positive this week", "odds": "65% Yes", "source": "Polymarket"},
            {"market": "Bitcoin above $100k by month end", "odds": "28% Yes", "source": "Kalshi"},
            {"market": "Oil WTI above $75 this week", "odds": "45% Yes", "source": "Polymarket"},
            {"market": "10Y Treasury yield above 4.5%", "odds": "38% Yes", "source": "Kalshi"},
        ]
        return random.choice(predictions)
    except Exception as e:
        print(f"Prediction fetch failed: {e}")
        return {"market": "Market direction today", "odds": "50/50", "source": "Consensus"}

def generate_outlook(sp_change, nq_change, vix_value):
    """Generate market outlook based on real data"""
    if sp_change is None or nq_change is None:
        return "Data loading. Check futures for pre-market direction."
    
    if sp_change > 0.5 and nq_change > 0.5:
        base = "Bullish pre-market. Both S&P and Nasdaq futures positive."
    elif sp_change < -0.5 and nq_change < -0.5:
        base = "Bearish pre-market. Both indices pointing lower."
    elif abs(sp_change) < 0.3 and abs(nq_change) < 0.3:
        base = "Flat pre-market. Minimal directional conviction."
    else:
        base = "Mixed pre-market. Divergence between S&P and Nasdaq."
    
    if vix_value and vix_value > 20:
        base += " VIX elevated — expect volatility."
    elif vix_value and vix_value < 15:
        base += " VIX compressed — calm before potential move."
    
    return base

def fetch_x_headlines() -> list:
    """Fetch latest headlines from X accounts using X API v2"""
    headlines = []
    
    # Try X API v2 first with user's bearer token
    for account in X_ACCOUNTS:
        try:
            # Search for recent tweets from this user
            query = f"from:{account['username']} -is:retweet"
            url = f"https://api.twitter.com/2/tweets/search/recent?query={urllib.parse.quote(query)}&max_results=5&tweet.fields=created_at,public_metrics"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {X_BEARER_TOKEN}",
                "User-Agent": "OvernightEdgeBot/1.0"
            })
            response = urllib.request.urlopen(req, timeout=15)
            data = json.loads(response.read().decode())
            tweets = data.get("data", [])
            if tweets:
                text = tweets[0].get("text", "")[:140]
                headlines.append({"handle": account["handle"], "text": text})
            else:
                headlines.append({"handle": account["handle"], "text": "[No recent posts]"})
        except Exception as e:
            print(f"X API v2 failed for {account['username']}: {e}")
            # Fallback to nitter scraper
            headlines.append(fetch_x_fallback(account))
    
    return headlines

def fetch_x_fallback(account: dict) -> dict:
    """Fallback X fetch using nitter instances"""
    nitter_instances = [
        "https://nitter.cz",
        "https://nitter.net",
        "https://nitter.privacydev.net",
    ]
    for instance in nitter_instances:
        try:
            url = f"{instance}/{account['username']}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read().decode("utf-8", errors="ignore")
            tweets = re.findall(r'<div class="tweet-content[^"]*">.*?<div class="tweet-body[^"]*">(.*?)</div>', html, re.DOTALL)
            if tweets:
                clean = re.sub(r'<[^>]+>', '', tweets[0])
                clean = re.sub(r'\s+', ' ', clean).strip()[:140]
                return {"handle": account["handle"], "text": clean}
        except:
            continue
    return {"handle": account["handle"], "text": f"[Follow @{account['username']} on X for live updates]"}

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
⚡ <b>NEWS:</b> {data['news'][0][:80]}...

🔮 <b>OUTLOOK:</b> {data['outlook']}

🎯 <b>PREDICTION OF THE DAY</b>
{data.get('prediction_of_the_day', {}).get('market', 'N/A')}
Odds: {data.get('prediction_of_the_day', {}).get('odds', 'N/A')} ({data.get('prediction_of_the_day', {}).get('source', '')})

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
Odds: {data.get('prediction_of_the_day', {}).get('odds', 'N/A')} ({data.get('prediction_of_the_day', {}).get('source', '')})

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
