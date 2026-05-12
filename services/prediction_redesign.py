"""
REDESIGNED PREDICTIONCORE & PREDICTION PRO REPORTS
==================================================
PredictionCore voice: Analytical, probabilistic, forecast-focused — like a quant analyst
Prediction Pro voice: Same but with "alert" urgency — like a prop desk getting hit
Content boundaries: ONLY prediction markets, probability divergences, consensus tracking
NO futures, NO congressional trades, NO short squeeze, NO X sentiment (except divergence)
"""

import random
from datetime import datetime, timezone

# Buy Button IDs
PC_BUY_BUTTON = "buy_btn_1TWLpXGrDuTtAB3mzRewSdxs"
PP_BUY_BUTTON = "buy_btn_1TWLouGrDuTtAB3mhwdzodZK"
LANDING_URL = "https://overnight-edge.vercel.app"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_dark.jpeg"

# Unique openings — never shared with other products
PC_OPENINGS = [
    "🔮 <b>PREDICTIONCORE — PROBABILITY WATCH</b>",
    "📊 <b>MARKETS OF OPINION</b>",
    "🎲 <b>WHERE THE CROWD IS WRONG</b>",
    "📈 <b>CONSENSUS VS REALITY</b>",
]

PP_OPENINGS = [
    "🚨 <b>PREDICTION PRO — SHIFT ALERT</b>",
    "⚡ <b>PROBABILITY SPIKE DETECTED</b>",
    "🔥 <b>MARKET MOVING ON BELIEF</b>",
    "🎯 <b>DIVERGENCE ALERT</b>",
]

# Prediction of the day rotation
PREDICTION_ROTATION = [
    "politics", "crypto", "macro", "sports", "culture", "weather"
]


def generate_prediction_core_report(prediction_of_the_day, market_pulse, crypto_pulse, divergence=None):
    """
    Generate PredictionCore report ($299 tier)
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    weekday = now.strftime("%A")
    
    opening = random.choice(PC_OPENINGS)
    
    divergence_section = ""
    if divergence:
        divergence_section = f"""
📊 <b>ARBITRAGE WATCH</b>
{divergence}
"""
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | {weekday}

🔮 <b>PREDICTION OF THE DAY</b>
{prediction_of_the_day}

━━━━━━━━━━━━━━━━━━━━
🌏 <b>MARKET PULSE</b>
{market_pulse}

━━━━━━━━━━━━━━━━━━━━
📡 <b>CRYPTO FLOW</b>
{crypto_pulse}
{divergence_section}
━━━━━━━━━━━━━━━━━━━━
💡 <b>WHAT IS PREDICTIONCORE?</b>
We track prediction markets (Polymarket, Kalshi, DraftKings) and identify where the crowd's probability diverges from reality. The edge is not in being right — it is in being right when the crowd is wrong.

{get_prediction_core_footer()}

⚠️ INFORMATIONAL ONLY — NOT FINANCIAL ADVICE"""
    
    return report


def generate_prediction_pro_report(shift_alert, new_markets, divergence_tracking, eod_summary):
    """
    Generate Prediction Pro report ($499 tier)
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    opening = random.choice(PP_OPENINGS)
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str}

🚨 <b>INSTANT SHIFT ALERT</b>
{shift_alert}

━━━━━━━━━━━━━━━━━━━━
📊 <b>NEW HIGH-VOLUME MARKETS</b>
{new_markets}

━━━━━━━━━━━━━━━━━━━━
🔍 <b>X SENTIMENT DIVERGENCE</b>
{divergence_tracking}

━━━━━━━━━━━━━━━━━━━━
📈 <b>END-OF-DAY SHIFT SUMMARY</b>
{eod_summary}

━━━━━━━━━━━━━━━━━━━━
💡 <b>WHY PREDICTION PRO?</b>
• Instant alerts on >5% probability moves
• New market detection before volume floods in
• X sentiment divergence tracking
• End-of-day probability shift reports
• Custom watchlists (coming soon)

PredictionCore gives you the daily read. Prediction Pro gives you the read before the market moves.

{get_prediction_pro_footer()}

⚠️ INFORMATIONAL ONLY — NOT FINANCIAL ADVICE"""
    
    return report


def get_prediction_core_footer():
    """Standard footer for PredictionCore"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Track probabilities daily →</b>
<a href="{LANDING_URL}">PredictionCore — $299/mo</a>
<b>Upgrade to Pro for instant alerts →</b>
<a href="{LANDING_URL}">Prediction Pro — $499/mo</a>
<b>See all tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


def get_prediction_pro_footer():
    """Standard footer for Prediction Pro"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Get instant shift alerts →</b>
<a href="{LANDING_URL}">Prediction Pro — $499/mo</a>
<b>Start with PredictionCore →</b>
<a href="{LANDING_URL}">PredictionCore — $299/mo</a>
<b>See all tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


# Integration helpers
PC_EXCLUDED_CONTENT = """
PredictionCore EXCLUDES:
- Pre-market futures (goes to Daily Digest)
- Congressional trades (goes to Signal Synthesizer)
- Insider filings (goes to Signal Synthesizer)
- Options flow (goes to Signal Synthesizer)
- Dark pool prints (goes to Signal Synthesizer)
- Short interest data (goes to Short Squeeze Radar)
- X/Twitter general sentiment (goes to X10/X20 Signal)
- Weekly outlook (goes to Sunday Setup)
"""
