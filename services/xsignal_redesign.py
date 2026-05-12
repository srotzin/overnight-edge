"""
REDESIGNED X10 SIGNAL & X20 SIGNAL REPORTS
==========================================
X10 voice: Social-native, fast, signal-dense — like a curated X feed with analysis
X20 voice: Full-spectrum authority — like a trading desk with every screen open
Content boundaries: ONLY X/Twitter signals, keyword confluence, cross-asset correlation
NO futures, NO congressional trades, NO prediction markets, NO short squeeze
"""

import random
from datetime import datetime, timezone

# Buy Button IDs
X10_BUY_BUTTON = "buy_btn_1TWLqtGrDuTtAB3m9vVOxud8"
X20_BUY_BUTTON = "buy_btn_1TWLqAGrDuTtAB3mBu2MrOMW"
LANDING_URL = "https://overnight-edge.vercel.app"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_dark.jpeg"

# Unique openings — never shared
X10_OPENINGS = [
    "📡 <b>X10 SIGNAL — SOCIAL INTELLIGENCE</b>",
    "🐦 <b>WHAT THE BIRDS ARE SAYING</b>",
    "💬 <b>X ALPHA SCAN</b>",
    "🔍 <b>KEYWORD CONFLUENCE ALERT</b>",
]

X20_OPENINGS = [
    "🌐 <b>X20 SIGNAL — FULL SPECTRUM</b>",
    "⚡ <b>CROSS-ASSET CORRELATION HIT</b>",
    "🎯 <b>INSTANT CONFLUENCE ALERT (4+)</b>",
    "📊 <b>X INTELLIGENCE DESK</b>",
]


def generate_x10_report(signals, keyword_matches):
    """
    Generate X10 Signal report ($249 tier)
    signals: list of dicts from top 20 X accounts
    keyword_matches: list of confluence hits
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M UTC")
    
    opening = random.choice(X10_OPENINGS)
    
    # Build signal lines
    signal_lines = []
    for s in signals[:5]:
        account = s.get("account", "unknown")
        ticker = s.get("ticker", "")
        sentiment = s.get("sentiment", "neutral")
        text_preview = s.get("text", "")[:80]
        
        emoji = "🟢" if sentiment == "bullish" else "🔴" if sentiment == "bearish" else "⚪"
        
        signal_lines.append(f"""  {emoji} <b>@{account}</b>{f' on ${ticker}' if ticker else ''}
     "{text_preview}..." """)
    
    signals_text = "\n".join(signal_lines) if signal_lines else "  No major signals from tracked accounts."
    
    # Build keyword confluence
    kw_lines = []
    for kw in keyword_matches[:3]:
        kw_lines.append(f"  🎯 <b>{kw.get('keyword', '')}</b>: {kw.get('count', 0)} mentions across {kw.get('accounts', 0)} accounts | Confluence: {kw.get('score', 0)}/5")
    
    kw_text = "\n".join(kw_lines) if kw_lines else "  No keyword confluence detected."
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | 🕐 {time_str}

📡 <b>TOP 20 ACCOUNT SCAN</b>
{signals_text}

━━━━━━━━━━━━━━━━━━━━
🎯 <b>KEYWORD CONFLUENCE</b>
{kw_text}

━━━━━━━━━━━━━━━━━━━━
💡 <b>WHAT IS X10?</b>
We scan 20 of the most followed trading accounts on X and score keyword matches across equities, commodities, FX, and derivatives. The signal is not the tweet — it is the pattern.

{get_x10_footer()}

⚠️ NOT FINANCIAL ADVICE"""
    
    return report


def generate_x20_report(signals, correlations, instant_alerts, eod_synthesis):
    """
    Generate X20 Signal report ($449 tier)
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M UTC")
    
    opening = random.choice(X20_OPENINGS)
    
    # Build correlation lines
    corr_lines = []
    for c in correlations[:3]:
        corr_lines.append(f"  🔗 <b>{c.get('asset1', '')}</b> ↔ <b>{c.get('asset2', '')}</b> | Correlation: {c.get('score', 0):.2f} | Signal: {c.get('direction', 'neutral')}")
    
    corr_text = "\n".join(corr_lines) if corr_lines else "  No significant cross-asset correlations detected."
    
    # Build instant alerts
    alert_lines = []
    for a in instant_alerts[:3]:
        alert_lines.append(f"  🚨 <b>{a.get('keyword', '')}</b>: Confluence {a.get('score', 0)}/5 | Assets: {', '.join(a.get('assets', []))}")
    
    alert_text = "\n".join(alert_lines) if alert_lines else "  No instant alerts triggered."
    
    report = f"""{opening}
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | 🕐 {time_str}

🚨 <b>INSTANT HIGH-CONFLUENCE ALERTS</b>
{alert_text}

━━━━━━━━━━━━━━━━━━━━
🔗 <b>CROSS-ASSET CORRELATION</b>
{corr_text}

━━━━━━━━━━━━━━━━━━━━
📡 <b>FULL SPECTRUM SCAN</b>
{signals}

━━━━━━━━━━━━━━━━━━━━
📊 <b>END-OF-DAY SYNTHESIS</b>
{eod_synthesis}

━━━━━━━━━━━━━━━━━━━━
💡 <b>WHAT IS X20?</b>
X20 is the full-spectrum upgrade from X10:
• Unlimited X account scanning (not just top 20)
• Cross-asset correlation scoring
• Instant alerts when confluence hits 4+
• 15-minute cadence during market hours
• Includes Short Squeeze Radar

{get_x20_footer()}

⚠️ NOT FINANCIAL ADVICE"""
    
    return report


def get_x10_footer():
    """Standard footer for X10 Signal"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Get X signals every 30 min →</b>
<a href="{LANDING_URL}">X10 Signal — $249/mo</a>
<b>Upgrade to X20 for full spectrum →</b>
<a href="{LANDING_URL}">X20 Signal — $449/mo</a>
<b>See all tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


def get_x20_footer():
    """Standard footer for X20 Signal"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Get full-spectrum X alerts →</b>
<a href="{LANDING_URL}">X20 Signal — $449/mo</a>
<b>Start with X10 →</b>
<a href="{LANDING_URL}">X10 Signal — $249/mo</a>
<b>See all tiers →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>"""


# Integration helpers
X10_EXCLUDED_CONTENT = """
X10 Signal EXCLUDES:
- Pre-market futures (goes to Daily Digest)
- Congressional trades (goes to Signal Synthesizer)
- Insider filings (goes to Signal Synthesizer)
- Options flow analysis (goes to Signal Synthesizer)
- Prediction markets (goes to PredictionCore)
- Short interest data (goes to Short Squeeze Radar)
- Weekly outlook (goes to Sunday Setup)
"""
