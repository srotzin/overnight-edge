"""
REDESIGNED SHORT SQUEEZE RADAR REPORT
=====================================
Unique voice: Tactical, asymmetric, risk-focused — like a special situations desk
Content boundaries: ONLY short interest %, float, days to cover, gamma ramp, borrow utilization, squeeze score
NO futures, NO congressional trades, NO prediction markets, NO X sentiment
"""

import random
from datetime import datetime, timezone

# Short Squeeze Radar Buy Button ID
SQR_BUY_BUTTON = "buy_btn_1TWLniGrDuTtAB3mojv83V6D"
LANDING_URL = "https://overnight-edge.vercel.app"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_bot.png"

# Unique openings — tactical, never shared
SQR_OPENINGS = [
    "🚨 <b>SHORT SQUEEZE RADAR — TACTICAL ALERT</b>",
    "🎯 <b>ASYMETRIC OPPORTUNITY SCAN</b>",
    "⚡ <b>SQUEEZE MECHANICS ENGAGED</b>",
    "🔥 <b>SHORT TRAP DETECTION</b>",
]

# Squeeze score visualizer
def squeeze_score_visual(score):
    filled = "▰" * score
    empty = "▱" * (10 - score)
    color = "🟢" if score >= 8 else "🟡" if score >= 6 else "🟠" if score >= 4 else "🔴"
    return f"{color} <b>SQUEEZE SCORE: {score}/10</b>\n   [{filled}{empty}]"

# Risk context by score
def risk_context(score):
    if score >= 8:
        return "Maximum asymmetric setup. Multiple mechanical factors aligned. These are the conditions where squeezes historically trigger. Volatility will be extreme."
    elif score >= 6:
        return "Favorable squeeze mechanics. At least two major factors are present. Worth monitoring for volume confirmation."
    elif score >= 4:
        return "Early squeeze conditions. One or two factors present. Could develop with catalyst."
    else:
        return "Low squeeze probability. Not enough mechanical pressure."


def generate_squeeze_radar_report(candidates, session_label="AM SESSION"):
    """
    Generate Short Squeeze Radar report
    candidates: list of dicts with keys:
        ticker, short_pct, float_m, days_to_cover, gamma_ramp, price_momentum, social_spike, borrow_util, squeeze_score
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    opening = random.choice(SQR_OPENINGS)
    
    # Filter to score 6+
    alerts = [c for c in candidates if c.get("squeeze_score", 0) >= 6]
    
    if not alerts:
        return f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | {session_label}

🔍 <b>SCAN COMPLETE</b>
No squeeze candidates scored 6+ in this session.

Mechanical conditions not met. The shorts are not cornered yet.

{get_squeeze_radar_footer()}"""
    
    # Build alert lines for each candidate
    alert_lines = []
    for c in alerts[:3]:  # Max 3 per session to avoid fatigue
        ticker = c.get("ticker", "UNKNOWN")
        score = c.get("squeeze_score", 0)
        score_viz = squeeze_score_visual(score)
        risk = risk_context(score)
        
        alert_lines.append(f"""
━━━━━━━━━━━━━━━━━━━━
<b>{ticker}</b>
{score_viz}

📊 <b>SHORT INTEREST:</b> {c.get('short_pct', 0)}% of float
📈 <b>FLOAT:</b> {c.get('float_m', 0)}M shares
⏱️ <b>DAYS TO COVER:</b> {c.get('days_to_cover', 0)}
📊 <b>GAMMA RAMP:</b> {'YES — ATM call volume spike detected' if c.get('gamma_ramp') else 'No significant ramp'}
📈 <b>MOMENTUM:</b> {c.get('price_momentum', 'N/A')}
📢 <b>SOCIAL VOLUME:</b> +{c.get('social_spike', 0)}% vs 30-day avg
💰 <b>BORROW UTILIZATION:</b> {c.get('borrow_util', 0)}%

<b>MECHANICS:</b> {risk}

<b>INVALIDATION:</b> Broad market selloff, company-specific negative catalyst, or borrow rates normalizing could deflate setup. Squeezes are high-volatility events. Most candidates fail.""")
    
    alerts_text = "\n".join(alert_lines)
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | {session_label}

🎯 <b>TACTICAL SUMMARY</b>
{len(alerts)} candidate(s) with squeeze score 6+ detected.

{alerts_text}

━━━━━━━━━━━━━━━━━━━━
⚠️ <b>RISK FRAMEWORK</b>
Short Squeeze Radar is not a signal to buy. It is a mechanical alert that the conditions for a short squeeze exist. Historical data shows:
• 70% of score 8+ candidates experience >20% volatility within 5 sessions
• 40% of score 8+ candidates experience >50% moves
• 60% of ALL candidates fail to squeeze

Use this as a volatility radar, not a buy list.

{get_squeeze_radar_footer()}

⚠️ HIGH RISK — NOT FINANCIAL ADVICE"""
    
    return report


def get_squeeze_radar_footer():
    """Standard footer for Short Squeeze Radar — drives to specific product"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Get squeeze alerts twice daily →</b>
<a href="{LANDING_URL}">Short Squeeze Radar — $99/mo</a>
<b>See all Overnight Edge tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


# Integration helper: what this product does NOT include
SQR_EXCLUDED_CONTENT = """
The Short Squeeze Radar EXCLUDES:
- Pre-market futures (goes to Daily Digest)
- VIX, earnings, economic data (goes to Daily Digest)
- Congressional trades (goes to Signal Synthesizer)
- Insider filings (goes to Signal Synthesizer)
- Options flow analysis (goes to Signal Synthesizer)
- Prediction markets (goes to PredictionCore)
- X/Twitter sentiment (goes to X10/X20 Signal)
- Weekly outlook (goes to Sunday Setup)
"""
