"""
REDESIGNED DAILY DIGEST REPORT
==============================
Unique voice: Authoritative, concise, pre-market focused
Content boundaries: ONLY futures, VIX, pre-market movers, overnight news, earnings, economic data
NO prediction markets, NO congressional trades, NO short squeeze, NO X sentiment
"""

import random
from datetime import datetime, timezone

# Daily Digest Buy Button ID
DD_BUY_BUTTON = "buy_btn_1TWLs4GrDuTtAB3mRdCm5bnZ"
LANDING_URL = "https://overnight-edge.vercel.app"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_dark.jpeg"

# Unique openings — never shared with other products
DD_OPENINGS = [
    "🌅 <b>THE OVERNIGHT EDGE — DAILY DIGEST</b>",
    "📈 <b>PRE-MARKET BRIEF</b>",
    "☕ <b>WHILE YOU SLEPT</b>",
    "🎯 <b>THE BELL APPROACHES</b>",
]

# Unique spicy takes — pre-market only, no overlap
DD_TAKES = [
    "Futures are pricing in a tone shift. Watch the cash open for confirmation.",
    "Overnight action suggests institutional repositioning. Volume will tell the truth.",
    "The pre-market narrative is set. Now we see if the market agrees.",
    "Quiet overnight = either confidence or complacency. The first 30 minutes decides.",
    "Gap up on thin volume is a trap until proven otherwise.",
]

# Unique closings — Daily Digest specific
DD_CLOSINGS = [
    "This is your Daily Digest. The full trading day awaits.",
    "See you at the open. Stay sharp.",
    "Pre-market edge delivered. Now execute.",
]


def generate_daily_digest_report(sp_futures, nq_futures, vix_value, vix_change, gainers, losers, headlines, earnings_today, economic_today):
    """Generate the Daily Digest report — PRE-MARKET ONLY, no overlap with other products"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    weekday = now.strftime("%A")
    
    opening = random.choice(DD_OPENINGS)
    take = random.choice(DD_TAKES)
    closing = random.choice(DD_CLOSINGS)
    
    # Format futures
    sp_str = f"{sp_futures.get('change_pct', 0):+.2f}%" if sp_futures else "N/A"
    nq_str = f"{nq_futures.get('change_pct', 0):+.2f}%" if nq_futures else "N/A"
    vix_str = f"{vix_value:.1f}" if vix_value else "N/A"
    vix_chg_str = f"{vix_change:+.1f}" if vix_change else "N/A"
    
    # Format gainers/losers
    gainer_lines = "\n".join([f"  📈 <b>{g['symbol']}</b>: {g['change_pct']:+.1f}%" for g in gainers[:5]]) if gainers else "  No significant pre-market movers."
    loser_lines = "\n".join([f"  📉 <b>{l['symbol']}</b>: {l['change_pct']:+.1f}%" for l in losers[:5]]) if losers else "  No significant pre-market decliners."
    
    # Format headlines
    headline_lines = "\n".join([f"  • {h}" for h in headlines[:5]]) if headlines else "  No major overnight headlines."
    
    # Format earnings
    earnings_lines = "\n".join([f"  📊 <b>{e['ticker']}</b>: EPS est ${e.get('eps', 'N/A')} | Rev est {e.get('rev', 'N/A')}" for e in earnings_today[:5]]) if earnings_today else "  No major earnings today."
    
    # Format economic
    economic_lines = "\n".join([f"  📅 <b>{e['time']}</b>: {e['event']} | Consensus: {e.get('consensus', 'N/A')}" for e in economic_today[:3]]) if economic_today else "  No major economic data today."
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | {weekday}

🌡️ <b>MARKET THERMAL</b>
{take}

📈 <b>FUTURES</b>
  S&amp;P 500 (ES): {sp_str}
  Nasdaq 100 (NQ): {nq_str}
  VIX: {vix_str} ({vix_chg_str})

🚀 <b>PRE-MARKET GAINERS</b>
{gainer_lines}

🔻 <b>PRE-MARKET LOSERS</b>
{loser_lines}

📰 <b>OVERNIGHT HEADLINES</b>
{headline_lines}

📊 <b>EARNINGS TODAY</b>
{earnings_lines}

📅 <b>ECONOMIC DATA</b>
{economic_lines}

━━━━━━━━━━━━━━━━━━━━
💬 {closing}

━━━━━━━━━━━━━━━━━━━━
<b>Get this every morning at 8:00 AM →</b>
<a href="{LANDING_URL}">Daily Digest — $49/mo</a>
<b>See all Overnight Edge tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>

⚠️ NOT FINANCIAL ADVICE"""
    
    return report


def get_daily_digest_footer():
    """Standard footer for Daily Digest — drives to specific product"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Get the Daily Digest every morning →</b>
<a href="{LANDING_URL}">Subscribe — $49/mo</a>
<b>See all Overnight Edge tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


# Integration helper: what this product does NOT include
DD_EXCLUDED_CONTENT = """
The Daily Digest EXCLUDES:
- Prediction markets (goes to PredictionCore)
- Congressional trades (goes to Signal Synthesizer)
- Insider filings (goes to Signal Synthesizer)
- Options flow (goes to Signal Synthesizer)
- Dark pool prints (goes to Signal Synthesizer)
- Short interest data (goes to Short Squeeze Radar)
- Squeeze scores (goes to Short Squeeze Radar)
- X/Twitter sentiment (goes to X10/X20 Signal)
- Weekly outlook (goes to Sunday Setup)
"""
