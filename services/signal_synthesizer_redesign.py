"""
REDESIGNED SIGNAL SYNTHESIZER REPORT
====================================
Unique voice: Insider, smart-money, institutional — like a hedge fund desk note
Content boundaries: ONLY congressional trades, SEC Form 4, unusual options flow, dark pool prints, confluence scoring
NO futures, NO prediction markets, NO short squeeze, NO X sentiment
"""

import random
from datetime import datetime, timezone

# Signal Synthesizer Buy Button ID
SS_BUY_BUTTON = "buy_btn_1TWLrSGrDuTtAB3muePQIrWx"
LANDING_URL = "https://overnight-edge.vercel.app"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_dark.jpeg"

# Unique openings — smart money, never shared
SS_OPENINGS = [
    "🦈 <b>SIGNAL SYNTHESIZER — SMART MONEY ALERT</b>",
    "💰 <b>THE INSIDER'S EDGE</b>",
    "🕳️ <b>DARK POOL PULSE</b>",
    "🏛️ <b>CONGRESSIONAL WATCH</b>",
]

# Confluence score badges
def confluence_badge(score):
    if score >= 5:
        return f"🎯 <b>CONFLUENCE {score}/5 — RARE ALIGNMENT</b>"
    elif score == 4:
        return f"🔥 <b>CONFLUENCE {score}/5 — HIGH CONFIDENCE</b>"
    elif score == 3:
        return f"⚡ <b>CONFLUENCE {score}/5 — MODERATE</b>"
    else:
        return f"📊 <b>CONFLUENCE {score}/5 — EARLY</b>"


def generate_signal_synthesizer_report(signals):
    """
    Generate Signal Synthesizer report
    signals: list of dicts with keys:
        ticker, signal_type (congressional/insider/options/darkpool),
        score (1-5), details, urgency
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    opening = random.choice(SS_OPENINGS)
    
    if not signals:
        return f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str}

🔍 <b>SCAN COMPLETE</b>
No signals met the 3/5 confluence threshold today.

This is the silence before the signal. The algos are watching.

{get_signal_synthesizer_footer()}"""
    
    # Sort by confluence score descending
    signals_sorted = sorted(signals, key=lambda x: x.get("score", 0), reverse=True)
    
    # Build signal lines
    signal_lines = []
    for s in signals_sorted[:5]:
        badge = confluence_badge(s.get("score", 0))
        sig_type = s.get("signal_type", "unknown")
        ticker = s.get("ticker", "UNKNOWN")
        details = s.get("details", "")
        urgency = s.get("urgency", "normal")
        
        urgency_emoji = "🚨" if urgency == "high" else "⚡" if urgency == "medium" else "📊"
        
        signal_lines.append(f"""
{urgency_emoji} <b>{ticker}</b> | {sig_type.upper()}
{badge}
{details}""")
    
    signals_text = "\n".join(signal_lines)
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str}

🔍 <b>SMART MONEY SCAN</b>
{len(signals)} signal(s) detected. Top {min(len(signals), 5)} by confluence:
{signals_text}

━━━━━━━━━━━━━━━━━━━━
💡 <b>WHAT IS CONFLUENCE?</b>
Signals score 1-5 based on how many independent smart-money indicators align:
• Congressional trade (STOCK Act)
• Insider filing (SEC Form 4)
• Unusual options flow
• Dark pool print
• Cross-reference validation

A 4/5 or 5/5 signal means multiple independent data sources are pointing the same direction. This does not guarantee outcomes — but it raises the probability.

{get_signal_synthesizer_footer()}

⚠️ NOT FINANCIAL ADVICE"""
    
    return report


def get_signal_synthesizer_footer():
    """Standard footer for Signal Synthesizer — drives to specific product"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Follow the smart money →</b>
<a href="{LANDING_URL}">Signal Synthesizer — $149/mo</a>
<b>See all Overnight Edge tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


# Integration helper: what this product does NOT include
SS_EXCLUDED_CONTENT = """
The Signal Synthesizer EXCLUDES:
- Pre-market futures (goes to Daily Digest)
- VIX, gainers/losers (goes to Daily Digest)
- Prediction markets (goes to PredictionCore)
- Short interest data (goes to Short Squeeze Radar)
- Squeeze scores (goes to Short Squeeze Radar)
- X/Twitter sentiment (goes to X10/X20 Signal)
- Weekly outlook (goes to Sunday Setup)
"""
