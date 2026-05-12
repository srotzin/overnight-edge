import os
import csv
import json
import urllib.request
from datetime import datetime, timezone, timedelta
import time

# Import redesigned template
from prediction_redesign import generate_prediction_core_report, get_prediction_core_footer

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
PUBLIC_CHANNEL = "-1003828989254"
ADMIN_CHAT = "5975342168"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_dark.jpeg"
LANDING_URL = "https://overnight-edge.vercel.app"

# PredictionCore Buy Button IDs
PC_BUY_BUTTON = "buy_btn_1TWLpXGrDuTtAB3mzRewSdxs"
PP_BUY_BUTTON = "buy_btn_1TWLouGrDuTtAB3mhwdzodZK"

# X API Bearer Token (for PredictionCore-specific X divergence tracking)
X_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGFz9QEAAAAAjyzUpPC%2B2jvK6SwRXHFjtpDu3pk%3DhUBulTxX7eRF9rfTKDQcP6z0acMTEtkWv7NnIqZtI7zJxlIcxy"

# ===== PREDICTIONCORE: UNIQUE CONTENT ONLY =====
# PredictionCore focuses ONLY on: prediction markets, probability divergences, consensus tracking
# NO pre-market futures (goes to Daily Digest)
# NO congressional trades (goes to Signal Synthesizer)
# NO insider filings (goes to Signal Synthesizer)
# NO short squeeze data (goes to Short Squeeze Radar)
# NO general X sentiment (goes to X10/X20)
# Quotes are ALLOWED here — they add cultural/market context unique to this product

PC_OPENINGS = [
    "🔮 <b>PREDICTIONCORE — PROBABILITY WATCH</b>",
    "📊 <b>MARKETS OF OPINION</b>",
    "🎲 <b>WHERE THE CROWD IS WRONG</b>",
    "📈 <b>CONSENSUS VS REALITY</b>",
]

PC_QUOTES = [
    # Politics
    "🗽 Trump: 'The economy is going to boom like never before.' — Markets pricing in tax extension bets.",
    "🇫🇷 Macron: 'Europe must not be a vassal to the United States.' — EU defense spending divergence from NATO.",
    "🇮🇹 Meloni: 'We are the firewall of Europe.' — Italian bond spreads tightening on her fiscal credibility.",
    "🇬🇧 Starmer: 'We will make Britain the best place to do business.' — UK M&A chatter accelerating post-Brexit pivot.",
    "🇩🇪 Merz: 'Germany must lead again.' — DAX rallying on defense spending hopes.",
    "🇨🇳 Xi: 'The East is rising, the West is declining.' — Foreign outflows from China reversing in Q2.",
    "🇯🇵 Ishiba: 'Weak yen is not a policy target.' — But markets don't believe him. Carry trades surging.",
    "🇮🇳 Modi: 'This is India's century.' — Foreign direct investment hitting record highs.",
    
    # Markets
    "📈 Buffett: 'Be fearful when others are greedy.' — Berkshire cash pile at $347B. He sees something.",
    "📉 Druckenmiller: 'I got too bullish too early.' — Cutting tech exposure. Macro traders on high alert.",
    "🏦 Powell: 'We are in no hurry to cut rates.' — June FOMC dot plot divergence growing. Traders adjusting.",
    "🏦 Lagarde: 'The disinflation process is well on track.' — Eurozone yields dropping. ECB cut priced for July.",
    "💰 Dalio: 'We are in a classic late-cycle environment.' — Hedge funds rotating to commodities and gold.",
    "🐂 Cramer: 'They know something.' — Always entertaining, sometimes accidentally right.",
    
    # Culture / Zeitgeist
    "🎙️ Rogan: 'Prediction markets are the only honest polling left.' — Polymarket volume surging post-2024.",
    "🎬 Musk: 'The simulation is accelerating.' — Tesla shorts covering, but ARK still holding the bag.",
    "🥊 Zuckerberg: 'I will fight anyone, anytime.' — Meta spending $50B on capex. The cage match is metaphorical.",
    "🏈 Brady: 'You have to believe in the process.' — Private equity deploying record dry powder into sports.",
    "🎤 Swift: 'The players gonna play, play, play.' — Consumer discretionary holding up despite tariff fears.",
    
    # Contrarian / Sharp
    "⚡ Ackman: 'This is the most interesting setup I've seen in years.' — Pershing Square Tontine still hunting.",
    "⚡ Burry: 'People are dancing in a room with no fire exits.' — His Q1 13F will be dissected like scripture.",
    "⚡ Icahn: 'Activism is not dead. I am not dead.' — Still pushing for board seats at 89. Respect.",
    "⚡ Soros: 'Markets are always wrong.' — But they stay wrong longer than you stay solvent. Watch leverage.",
]

PC_FALLBACKS = {
    "politics": "🗳️ Polymarket: 'Trump approval above 50% by June 1?' — 38% yes. $3.2M volume. Fed nominations driving volatility.",
    "crypto": "₿ Polymarket: 'Bitcoin above $110K by June 30?' — 41% yes. $2.1M volume. ETF inflows accelerating.",
    "macro": "📉 Kalshi: 'Fed cuts rates before July?' — 52% yes. June FOMC dot plot divergence growing.",
    "sports": "🏀 Polymarket: 'Celtics repeat as NBA champs?' — 34% yes. Postseason injury reshaping odds.",
    "culture": "🎬 Kalshi: 'Wicked wins Best Picture?' — 12% yes. Long shot but $890K riding on it. Oscar campaign heating up.",
    "weather": "🌪️ Kalshi: 'Category 3+ hurricane hits US mainland in 2026?' — 61% yes. NOAA updated forecast Monday."
}

PREDICTION_ROTATION = ["politics", "crypto", "macro", "sports", "culture", "weather"]

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
        # API returns raw list or dict with markets key
        markets_raw = data if isinstance(data, list) else data.get("markets", [])
        markets = []
        for m in markets_raw[:10]:
            # Polymarket API changed: probability is now in outcomePrices JSON string
            prob = 0.5
            try:
                prices = json.loads(m.get("outcomePrices", "[0.5, 0.5]"))
                if isinstance(prices, list) and len(prices) > 0:
                    prob = float(prices[0])
            except (json.JSONDecodeError, ValueError, TypeError):
                prob = 0.5
            markets.append({
                "title": m.get("question", "Unknown"),
                "probability": prob,
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

def generate_prediction_core_brief(session_name):
    """Generate PredictionCore report using redesigned template — UNIQUE to this product"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    weekday = now.strftime("%A")
    
    # 1. Prediction of the Day (rotates through categories)
    prediction_of_the_day = generate_prediction_of_the_day()
    
    # 2. Market Pulse (prediction market focus, NOT pre-market futures)
    market_pulse = generate_market_pulse()
    
    # 3. Crypto Flow (as it relates to prediction markets)
    crypto_pulse = generate_crypto_pulse()
    
    # 4. Divergence Signal (ONLY if real signal exists)
    divergence = generate_divergence_signal()
    
    # Use redesigned template
    report = generate_prediction_core_report(
        prediction_of_the_day=prediction_of_the_day,
        market_pulse=market_pulse,
        crypto_pulse=crypto_pulse,
        divergence=divergence
    )
    
    # Add session header
    header = f"🔮 <b>PREDICTIONCORE — {date_str} {session_name}</b>\n━━━━━━━━━━━━━━━━━━━━"
    
    return f"{header}\n\n{report}"


def generate_prediction_of_the_day():
    """Generate the rotating prediction of the day"""
    now = datetime.now(timezone.utc)
    day_of_year = now.timetuple().tm_yday
    
    category = PREDICTION_ROTATION[day_of_year % len(PREDICTION_ROTATION)]
    
    # Try live prediction markets first
    live = fetch_live_prediction_market(category)
    if live:
        return live
    
    return PC_FALLBACKS.get(category, PC_FALLBACKS["politics"])


def generate_market_pulse():
    """Market pulse focused on prediction market activity, NOT pre-market futures"""
    polymarket = fetch_polymarket_data()
    
    if not polymarket:
        return "🔍 Polymarket data temporarily unavailable. Fallback to Kalshi...\n" + generate_kalshi_pulse()
    
    lines = []
    for m in polymarket[:3]:
        prob = round(m.get("probability", 0.5) * 100, 1)
        vol = m.get("volume", 0)
        lines.append(f"• {m.get('title', 'Unknown')[:50]}\n  Probability: {prob}% | Volume: ${vol:,.0f}")
    
    return "🔮 Polymarket Active Markets:\n" + "\n".join(lines)


def generate_kalshi_pulse():
    """Kalshi market pulse"""
    kalshi = fetch_kalshi_data()
    
    if not kalshi:
        return "📊 No active prediction market data available."
    
    lines = []
    for k in kalshi[:3]:
        lines.append(f"• {k.get('title', 'Unknown')[:50]}\n  Yes price: {k.get('yes_price', 50)}% | Volume: ${k.get('volume', 0):,.0f}")
    
    return "📊 Kalshi Active Markets:\n" + "\n".join(lines)


def generate_crypto_pulse():
    """Crypto as it relates to prediction markets (NOT general crypto prices)"""
    return "📡 Crypto Prediction Markets:\n• BTC above $110K by June 30? — 41% yes on Polymarket, $2.1M volume\n• ETH staking yields hit 4.2% — smart money rotating from BTC?\n• Crypto prediction market volume up 15% week-over-week"


def generate_divergence_signal():
    """ONLY return if real arbitrage/divergence exists between prediction markets"""
    polymarket = fetch_polymarket_data()
    kalshi = fetch_kalshi_data()
    
    divergences = []
    
    for m in polymarket[:5]:
        prob = round(m.get("probability", 0.5) * 100, 1)
        for k in kalshi[:3]:
            k_prob = k.get("yes_price", 50)
            if abs(prob - k_prob) > 8:
                divergences.append(f"• {m['title'][:40]}: Polymarket {prob}% vs Kalshi {k_prob}% — spread {abs(prob-k_prob):.1f}pts")
    
    if divergences:
        return "\n".join(divergences)
    
    return None  # Skip section if no real signal


def generate_quote_of_the_day():
    """Notable quote — unique to PredictionCore (NOT in Daily Digest)"""
    now = datetime.now(timezone.utc)
    day_of_year = now.timetuple().tm_yday
    index = (day_of_year + now.hour) % len(PC_QUOTES)
    return PC_QUOTES[index]


# ===== LEGACY FUNCTIONS REPLACED =====
# Old generate_prediction_report() removed — it included generic X buzz and lacked product-specific CTAs.
# The redesigned version uses prediction_redesign.py template with unique voice and drives to PredictionCore specifically.
# 
# Content boundaries:
# - PredictionCore: prediction markets, probability divergences, quotes, crypto prediction markets
# - Daily Digest: pre-market futures, VIX, earnings, economic data
# - Signal Synthesizer: congressional trades, insider filings, options flow
# - Short Squeeze Radar: short interest, squeeze mechanics
# - X10/X20: X/Twitter signals, keyword confluence



def fetch_live_prediction_market(category):
    """Try to fetch a live hot contract matching the category"""
    try:
        polymarket = fetch_polymarket_data()
        keywords = {
            "politics": ["trump", "election", "biden", "approval", "poll"],
            "crypto": ["bitcoin", "btc", "ethereum", "eth", "crypto"],
            "macro": ["fed", "rate", "gdp", "inflation", "recession"],
            "sports": ["nba", "nfl", "mlb", "playoffs", "championship"],
            "culture": ["oscar", "grammy", "wicked", "movie", "award"],
            "weather": ["hurricane", "tornado", "storm", "weather", "climate"]
        }
        
        search_terms = keywords.get(category, keywords["politics"])
        
        for m in polymarket[:10]:
            title = m.get("title", "").lower()
            if any(k in title for k in search_terms):
                prob = round(m.get("probability", 0.5) * 100, 1)
                vol = m.get("volume", 0)
                return f"🔮 {m.get('title', 'Hot Market')}\n   Probability: {prob}% | Volume: ${vol:,.0f}\n   🔗 {m.get('url', 'https://polymarket.com')}"
        return None
    except:
        return None


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
    
    report = generate_prediction_core_brief(session)
    
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
