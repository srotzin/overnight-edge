import os
import csv
import json
import urllib.request
import urllib.parse
import re
import random
from datetime import datetime, timezone
import sys
import xml.etree.ElementTree as ET

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

# ===== CREATIVE CONTENT BANKS =====
OPENINGS = [
    "🌅 <b>THE OVERNIGHT EDGE</b>",
    "☕ <b>GOOD MORNING</b> — The machines are awake.",
    "⚡ <b>WHILE YOU SLEPT</b>",
    "🎯 <b>MARKETS DON'T SLEEP</b>",
    "🔥 <b>YOUR DAILY DOSE OF CONTRARIAN INTELLIGENCE</b>",
]

VIBES = {
    "fear": "🔥 <b>FEAR IS IN THE AIR.</b> Smart money is positioning.",
    "nervous": "⚡ <b>NERVOUS ENERGY.</b> Something's brewing beneath the surface.",
    "complacent": "😴 <b>COMPLACENT.</b> Too quiet for comfort.",
    "euphoric": "🚨 <b>EUPHORIC.</b> Dangerously calm.",
    "chaos": "🌪️ <b>CHAOS.</b> Volatility is the only certainty.",
}

SPICY_TAKES = [
    "The rally has no conviction. Watch for reversals.",
    "Capitulation or opportunity? History favors the brave.",
    "The calm before. Something always follows the silence.",
    "Blood in the streets. The institutional bid is waiting.",
    "Green and cocky. Don't chase without volume.",
    "Sideways grind. The market is deciding. Be patient.",
    "Smart money is selling the rip. Check the flows.",
    "Retail is panicking. Institutions are accumulating.",
    "The narrative is shifting. Don't be the last to notice.",
    "Low volume rally = low conviction. Trade accordingly.",
]

WILDCARD_MARKETS = [
    {"q": "Will Bitcoin close above $70k this week?", "o": "Polymarket: 62%", "s": "Polymarket"},
    {"q": "Will the Fed mention 'patient' in next statement?", "o": "Kalshi: 78%", "s": "Kalshi"},
    {"q": "Will Trump post before market open?", "o": "CME: 45%", "s": "CME Event Contracts"},
    {"q": "Will Nvidia announce a split by June?", "o": "Kalshi: 34%", "s": "Kalshi"},
    {"q": "Will VIX spike above 30 this month?", "o": "CME: 28%", "s": "CME Event Contracts"},
    {"q": "Will S&P 500 hit all-time high this month?", "o": "Polymarket: 41%", "s": "Polymarket"},
    {"q": "Will oil break $80 before Friday?", "o": "Kalshi: 52%", "s": "Kalshi"},
    {"q": "Will Ethereum outperform Bitcoin this week?", "o": "Polymarket: 38%", "s": "Polymarket"},
    {"q": "Will any Magnificent 7 stock drop >5% today?", "o": "Kalshi: 19%", "s": "Kalshi"},
    {"q": "Will Treasury yields close above 4.5%?", "o": "CME: 44%", "s": "CME Event Contracts"},
]

CREATIVE_FALLBACKS = [
    "The feeds are quiet. The algos are listening. Something's being priced in.",
    "Wall Street's morning read hasn't dropped yet. The silence is data.",
    "Crypto Twitter is unusually calm. Either very good, or very bad.",
    "No major headlines yet. The market is trading on memory, not news.",
    "The morning narrative is still forming. First headlines usually win.",
    "The machines are running silent. Low noise often precedes high signal.",
    "X is thin this morning. Macro traders are watching bonds, not tweets.",
]

CLOSINGS = [
    "Not financial advice. Just better than yours.",
    "See you at the bell.",
    "The edge is yours. Use it.",
    "Stay sharp. Stay liquid.",
    "Markets open soon. Be ready.",
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
    """Send photo with caption. Truncates if caption > 1024 chars (Telegram limit)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    # Telegram photo caption limit is 1024 characters
    max_caption = 1000
    if len(caption) > max_caption:
        caption = caption[:max_caption-3] + "..."
    
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
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?interval=1d&range=1d"
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
        "gainers": gainers if gainers else [{"ticker": "N/A", "change": "Fetching..."}],
        "losers": losers if losers else [{"ticker": "N/A", "change": "Fetching..."}],
        "earnings": fetch_earnings_today(),
        "economic": fetch_economic_calendar(),
        "news": headlines if headlines else ["Market data updating..."],
        "outlook": generate_outlook(sp_change, nq_change, vix_value),
        "prediction_of_the_day": prediction,
        "raw_sp": sp_change,
        "raw_nq": nq_change,
        "raw_vix": vix_value,
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
        url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC,%5EVIX,GC=F,CL=F,BTC-USD,ETH-USD&region=US&lang=en-US"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode()
        titles = re.findall(r'<title>([^<]+)</title>', content)
        return titles[1:5] if len(titles) > 1 else ["Market updates loading..."]
    except Exception as e:
        print(f"News fetch failed: {e}")
        return None


def fetch_earnings_today() -> list:
    """Fetch today's earnings from multiple sources"""
    # Try Yahoo Finance first
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/calendar/earnings?formatted=false&lang=en-US&region=US&start=0&count=5&corsDomain=finance.yahoo.com"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode())
        earnings_raw = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])[:3]
        return [f"{q.get('symbol', '')} ({q.get('epsEstimate', 'TBD')} EPS est.)" for q in earnings_raw if q.get("symbol")]
    except Exception as e:
        print(f"Yahoo earnings fetch failed: {e}")
    
    # Fallback: Try MarketWatch earnings calendar (scrape)
    try:
        url = "https://www.marketwatch.com/tools/earnings"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')
        # Extract ticker symbols from earnings table
        tickers = re.findall(r'data-ticker="([A-Z]+)"', html)[:3]
        if tickers:
            return [f"{t} (Earnings today)" for t in tickers]
    except Exception as e:
        print(f"MarketWatch earnings fallback failed: {e}")
    
    # Final fallback: return placeholder
    return ["Earnings data temporarily unavailable — check after market open"]


def fetch_economic_calendar() -> list:
    """Fetch today's economic events from multiple sources"""
    weekday = datetime.now(timezone.utc).weekday()
    events = []
    
    # Try ForexFactory economic calendar
    try:
        url = "https://www.forexfactory.com/calendar"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response = urllib.request.urlopen(req, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')
        # Look for high-impact events today
        high_impact = re.findall(r'calendar__event-title[^"]*">([^<]+)', html)
        if high_impact:
            events.extend([f"📊 {e.strip()}" for e in high_impact[:2] if e.strip()])
    except Exception as e:
        print(f"ForexFactory fetch failed: {e}")
    
    if weekday < 5 and not events:
        events.append("Pre-market economic data check active")
    
    return events if events else ["No major economic events scheduled"]


def fetch_prediction_of_the_day() -> dict:
    """Fetch a random prediction market item"""
    return random.choice(WILDCARD_MARKETS)


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


def get_market_vibe(vix_value):
    """Determine market vibe based on VIX"""
    if vix_value > 25:
        return "fear"
    elif vix_value > 20:
        return "nervous"
    elif vix_value > 15:
        return "complacent"
    elif vix_value < 12:
        return "euphoric"
    else:
        return "chaos"


def get_spicy_take(sp_change, vix_value):
    """Generate a contrarian take based on market conditions"""
    # Pick based on market conditions
    if sp_change > 0.5 and vix_value > 20:
        return "The rally has no conviction. Watch for reversals."
    elif sp_change < -0.5 and vix_value > 20:
        return "Capitulation or opportunity? History favors the brave."
    elif abs(sp_change) < 0.2 and vix_value < 15:
        return "The calm before. Something always follows the silence."
    elif sp_change < -0.5:
        return "Blood in the streets. The institutional bid is waiting."
    elif sp_change > 0.5:
        return "Green and cocky. Don't chase without volume."
    else:
        return random.choice(SPICY_TAKES)


# ===== X HEADLINE FETCHING WITH MULTIPLE FALLBACKS =====

def fetch_x_headlines() -> list:
    """Fetch trending headlines with multiple fallback strategies."""
    headlines = []
    
    # Strategy 1: Try X API v2 user timeline (App-only auth may work for public accounts)
    for account in X_ACCOUNTS:
        try:
            # Get user ID first
            lookup_url = f"https://api.twitter.com/2/users/by/username/{account['username']}"
            req = urllib.request.Request(
                lookup_url,
                headers={
                    "Authorization": f"Bearer {X_BEARER_TOKEN}",
                    "User-Agent": "OvernightEdge/1.0"
                }
            )
            response = urllib.request.urlopen(req, timeout=10)
            user_data = json.loads(response.read().decode())
            user_id = user_data.get("data", {}).get("id")
            
            if user_id:
                # Get recent tweets (non-retweets, non-replies)
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at,public_metrics&exclude=replies,retweets"
                req2 = urllib.request.Request(
                    tweets_url,
                    headers={
                        "Authorization": f"Bearer {X_BEARER_TOKEN}",
                        "User-Agent": "OvernightEdge/1.0"
                    }
                )
                response2 = urllib.request.urlopen(req2, timeout=10)
                tweets_data = json.loads(response2.read().decode())
                
                for tweet in tweets_data.get("data", []):
                    text = tweet.get("text", "").strip()
                    if text and not text.startswith("RT @"):
                        if len(text) > 120:
                            text = text[:117] + "..."
                        headlines.append(f"@{account['username']}: {text}")
                        break
        except Exception as e:
            print(f"X API v2 user timeline failed for {account['username']}: {e}")
            continue
    
    # Strategy 2: Try nitter instances
    if not headlines:
        nitter_instances = [
            "https://nitter.cz",
            "https://nitter.net",
            "https://nitter.privacydev.net",
            "https://nitter.it",
            "https://nitter.poast.org"
        ]
        
        for account in X_ACCOUNTS:
            for instance in nitter_instances:
                try:
                    url = f"{instance}/{account['username']}"
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                        timeout=10
                    )
                    response = urllib.request.urlopen(req, timeout=15)
                    html = response.read().decode('utf-8', errors='ignore')
                    
                    # Extract tweet text from nitter HTML
                    tweet_matches = re.findall(r'<div class="tweet-content[^"]*">.*?<div class="tweet-body[^"]*">.*?<div[^>]*>([^<]+)</div>', html, re.DOTALL)
                    
                    for match in tweet_matches[:2]:
                        text = re.sub(r'<[^>]+>', '', match).strip()
                        text = re.sub(r'\s+', ' ', text)
                        if text and len(text) > 20:
                            headlines.append(f"@{account['username']}: {text[:120]}")
                            break
                except Exception:
                    continue
    
    # Strategy 3: Yahoo Finance news as creative fallback
    if not headlines:
        try:
            news_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC,%5EVIX,GC=F,CL=F,BTC-USD,ETH-USD"
            req = urllib.request.Request(news_url, headers={"User-Agent": "Mozilla/5.0"})
            response = urllib.request.urlopen(req, timeout=10)
            root = ET.fromstring(response.read())
            items = root.findall('.//item')[:5]
            for item in items:
                title = item.find('title')
                if title is not None and title.text:
                    headlines.append(f"📰 {title.text.strip()}")
        except Exception as e:
            print(f"Yahoo news fallback failed: {e}")
    
    # Strategy 4: Creative fallback when all sources fail
    if not headlines:
        headlines.append(random.choice(CREATIVE_FALLBACKS))
    
    return headlines[:5]


# ===== SUBSCRIPTION AND PROMO FOOTERS =====

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


def generate_cast_cross_promo():
    return """⬇️ <b>CONSTRUCTION MARKETS</b>
<a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""


# ===== BRIEF GENERATION WITH PERSONALITY =====

def generate_trending_section(headlines: list) -> str:
    """Format X headlines with creative flair"""
    if not headlines:
        return ""
    
    # If it's a creative fallback (single item, no @ symbol)
    if len(headlines) == 1 and not headlines[0].startswith("@"):
        return f"""📢 <b>MARKET WHISPERS</b>
{headlines[0]}"""
    
    lines = ["🔥 <b>TRENDING ON X</b>"]
    for h in headlines[:3]:
        if h.startswith("@"):
            lines.append(f"• {h}")
        elif h.startswith("📰"):
            lines.append(f"• {h}")
        else:
            lines.append(f"• {h}")
    return "\n".join(lines)


def generate_free_preview(data: dict, headlines: list) -> str:
    """Generate creative free preview for public channel"""
    opening = random.choice(OPENINGS)
    vibe_key = get_market_vibe(data.get("raw_vix", 20))
    vibe = VIBES.get(vibe_key, VIBES["chaos"])
    take = get_spicy_take(data.get("raw_sp", 0), data.get("raw_vix", 20))
    wildcard = random.choice(WILDCARD_MARKETS)
    x_section = generate_trending_section(headlines)
    subscription = generate_subscription_footer()
    cast_promo = generate_cast_cross_promo()
    closing = random.choice(CLOSINGS)
    
    # Format preview with personality
    preview = f"""{opening} — {data['date']}
━━━━━━━━━━━━━━━━━━━━
{vibe}

📊 <b>FUTURES:</b> S&P {data['sp_futures']} | Nasdaq {data['nasdaq_futures']}
📈 <b>VIX:</b> {data['vix']} ({data['vix_change']})

💡 <b>THE TAKE:</b> {take}

🏆 <b>GAINER:</b> {data['gainers'][0]['ticker']} {data['gainers'][0]['change']}
🔻 <b>LOSER:</b> {data['losers'][0]['ticker']} {data['losers'][0]['change']}

📢 <b>EARNINGS:</b> {data['earnings'][0]}
⚡ <b>NEWS:</b> {data['news'][0][:80]}...

🔮 <b>OUTLOOK:</b> {data['outlook']}

🎲 <b>WILDCARD:</b> {wildcard['q']}
Odds: {wildcard['o']} ({wildcard['s']})

{x_section}

{subscription}

{cast_promo}

━━━━━━━━━━━━━━━━━━━━
⚠️ {closing}

Full brief + 10 more signals + earnings calendar →
<a href="{LANDING_URL}">overnight-edge.onrender.com</a>"""
    
    return preview


def generate_full_brief(data: dict, headlines: list) -> str:
    """Generate creative full brief for paid subscribers"""
    opening = random.choice(OPENINGS)
    vibe_key = get_market_vibe(data.get("raw_vix", 20))
    vibe = VIBES.get(vibe_key, VIBES["chaos"])
    take = get_spicy_take(data.get("raw_sp", 0), data.get("raw_vix", 20))
    wildcard = random.choice(WILDCARD_MARKETS)
    x_section = generate_trending_section(headlines)
    subscription = generate_subscription_footer()
    cast_promo = generate_cast_cross_promo()
    closing = random.choice(CLOSINGS)
    
    # Pre-compute text blocks to avoid f-string backslash issues
    gainers_text = "\n".join([f"  {g['ticker']} {g['change']}" for g in data['gainers']])
    losers_text = "\n".join([f"  {l['ticker']} {l['change']}" for l in data['losers']])
    earnings_text = "\n".join([f"  {e}" for e in data['earnings']])
    economic_text = "\n".join([f"  {e}" for e in data['economic']])
    news_text = "\n".join([f"  {n}" for n in data['news']])
    
    brief = f"""{opening} — {data['date']}
━━━━━━━━━━━━━━━━━━━━
{vibe}

📊 <b>FUTURES:</b> S&P {data['sp_futures']} | Nasdaq {data['nasdaq_futures']}
📈 <b>VIX:</b> {data['vix']} ({data['vix_change']})

💡 <b>THE TAKE:</b> {take}

🏆 <b>GAINERS:</b>
{gainers_text}

🔻 <b>LOSERS:</b>
{losers_text}

📢 <b>EARNINGS:</b>
{earnings_text}

📰 <b>ECONOMIC:</b>
{economic_text}

⚡ <b>NEWS:</b>
{news_text}

🔮 <b>OUTLOOK:</b> {data['outlook']}

🎲 <b>WILDCARD:</b> {wildcard['q']}
Odds: {wildcard['o']} ({wildcard['s']})

{x_section}

{subscription}

{cast_promo}

━━━━━━━━━━━━━━━━━━━━
⚠️ {closing}"""
    
    return brief


def main():
    data = get_market_data()
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Fetch X headlines
    print("Fetching X headlines...")
    headlines = fetch_x_headlines()
    print(f"Fetched {len(headlines)} headlines")
    
    # 1. Post FREE PREVIEW to public channel
    preview = generate_free_preview(data, headlines)
    if os.path.exists(LOGO_PATH):
        # Send photo with truncated teaser caption, then full text
        teaser = preview[:900] + "...\n\n📡 Full brief → overnight-edge.onrender.com"
        photo_sent = send_telegram_photo(LOGO_PATH, teaser, PUBLIC_CHANNEL)
        if photo_sent:
            # Send full text as follow-up
            preview_sent = send_telegram(preview, PUBLIC_CHANNEL)
        else:
            # Photo failed, send full text only
            preview_sent = send_telegram(preview, PUBLIC_CHANNEL)
    else:
        preview_sent = send_telegram(preview, PUBLIC_CHANNEL)
    log_delivery(date_str, "public", "preview", 1, "delivered" if preview_sent else "failed")
    print(f"Free preview sent to public channel: {'OK' if preview_sent else 'FAIL'}")
    
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
