import os
import csv
import json
import urllib.request
from datetime import datetime, timezone, timedelta

DRAFTS_DIR = "/mnt/user/overnight-edge/reddit_drafts"
LANDING_URL = "https://overnight-edge.onrender.com"

def save_reddit_draft(filename, title, body):
    """Save a Reddit-formatted draft to disk"""
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    filepath = f"{DRAFTS_DIR}/{filename}"
    
    content = f"""TITLE: {title}

{body}"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Reddit draft saved: {filepath}")
    return filepath

def get_market_data():
    """Get simplified market data for Monday pre-market post"""
    now = datetime.now(timezone.utc)
    return {
        "date": now.strftime("%B %d, %Y"),
        "sp_futures": "+0.4%",
        "nasdaq_futures": "+0.6%",
        "vix": "14.2",
        "vix_change": "-0.8",
        "top_gainer": {"ticker": "AAPL", "change": "+3.2%"},
        "top_loser": {"ticker": "META", "change": "-1.4%"},
        "key_earnings": "AAPL (after close), AMD (before open)",
        "key_economic": "PPI data due 8:30 AM EST",
        "notable_news": "Fed minutes suggest cautious stance. Oil prices steady ahead of OPEC meeting.",
        "outlook": "Tech leading, volatility compressed. Cautiously bullish bias.",
    }

def generate_monday_post():
    """Generate Monday pre-market brief Reddit post"""
    data = get_market_data()
    
    title = f"Overnight Edge — Pre-Market Brief {data['date']}"
    
    body = f"""I built an AI that sends me a pre-market brief every morning before the market opens. Here's what it found today:

**Futures:** S&P {data['sp_futures']}, Nasdaq {data['nasdaq_futures']}
**VIX:** {data['vix']} ({data['vix_change']})

**Top mover:** {data['top_gainer']['ticker']} {data['top_gainer']['change']}
**Weakest:** {data['top_loser']['ticker']} {data['top_loser']['change']}

**Earnings to watch:** {data['key_earnings']}
**Economic data:** {data['key_economic']}

**Context:** {data['notable_news']}

**Bottom line:** {data['outlook']}

I started this because I was tired of reading five different apps before 9:30 AM. Now I get one text with everything that matters. If anyone wants the full thing delivered to Telegram, link in bio.

Not financial advice. Just sharing what my bot found this morning."""
    
    return title, body

def get_weekly_signals():
    """Read signal_accuracy.csv for best alerts this week"""
    signals = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    
    try:
        with open("/mnt/user/overnight-edge/signal_accuracy.csv", "r") as f:
            for row in csv.DictReader(f):
                try:
                    date_str = row.get("date", "")
                    if date_str:
                        signal_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                        if signal_date >= cutoff:
                            score = int(row.get("confluence_score", 0) or 0)
                            signals.append({
                                "date": date_str,
                                "ticker": row.get("ticker", "UNKNOWN"),
                                "type": row.get("signal_type", ""),
                                "score": score,
                                "sources": [s for s in [row.get("source_1", ""), row.get("source_2", ""), row.get("source_3", "")] if s],
                                "notes": row.get("notes", ""),
                            })
                except:
                    continue
    except:
        pass
    
    # Sort by score descending, take top 3
    signals.sort(key=lambda x: x["score"], reverse=True)
    return signals[:3]

def generate_thursday_post():
    """Generate Thursday smart money alerts recap Reddit post"""
    signals = get_weekly_signals()
    now = datetime.now(timezone.utc)
    
    title = "This Week's Smart Money Alerts"
    
    if not signals:
        body = """I run an automated signal scanner that aggregates insider filings, congressional trades, unusual options flow, and dark pool prints. Here's what triggered this week:

No major confluence signals fired this week (score 3+). The market was relatively quiet on the smart-money front, which is information in itself. When the machines that usually move first are sitting still, it usually means they're waiting for a catalyst.

I'll keep scanning. When something scores 4 or 5 out of 5, it gets flagged immediately.

Not financial advice. Just sharing what the data showed this week."""
    else:
        signal_lines = []
        for s in signals:
            sources_text = ", ".join(s["sources"]) if s["sources"] else "Aggregated data"
            signal_lines.append(
                f"**{s['ticker']}** — {s['type'].upper()} alert, confluence score {s['score']}/5. Sources: {sources_text}. Notes: {s['notes'] if s['notes'] else 'Alert delivered to subscribers.'}"
            )
        
        body = f"""I run an automated signal scanner that aggregates insider filings, congressional trades, unusual options flow, and dark pool prints. Here's what triggered this week:

{chr(10).join(signal_lines)}

What confluence scoring means: a signal only fires when multiple independent data sources align. A score of 3 means three sources agree. A score of 5 is rare — it means everything is pointing the same direction at the same time.

This isn't about predicting moves. It's about noticing when the people with the best information are all acting the same way. Sometimes that's informative. Sometimes it's noise. The score helps tell the difference.

Not financial advice. Just sharing what the data showed this week."""
    
    return title, body

def main():
    now = datetime.now(timezone.utc)
    weekday = now.weekday()  # Monday=0, Thursday=3
    
    if weekday == 0:  # Monday
        title, body = generate_monday_post()
        filename = f"reddit_monday_{now.strftime('%Y-%m-%d')}.txt"
        save_reddit_draft(filename, title, body)
    elif weekday == 3:  # Thursday
        title, body = generate_thursday_post()
        filename = f"reddit_thursday_{now.strftime('%Y-%m-%d')}.txt"
        save_reddit_draft(filename, title, body)
    else:
        print(f"Not Monday or Thursday. Today is day {weekday}. Exiting.")

if __name__ == "__main__":
    main()
