"""
REDESIGNED CAST REPORT ALERT
============================
Unique voice: Construction industry professional, data-driven, supply-chain focused
Content boundaries: ONLY Simpson Strong-Tie embed data: STHD, SSTB, MASA, state-by-state
NO financial market content — this is entirely separate from Overnight Edge
"""

from datetime import datetime, timezone

CAST_LANDING_URL = "https://castreport.com"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_bot.png"


def generate_cast_alert(analysis, previous_data=None):
    """
    Generate CAST Report alert
    analysis: dict with keys:
        anomalies, top_states, total_states, total_amount, total_count,
        sthd_total, sstb_total, masa_total
    previous_data: optional previous day analysis for comparison
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Build anomaly lines
    if analysis.get("anomalies"):
        anomaly_lines = "\n".join([f"  {a['direction']} <b>{a['state']}</b>: {a['change']} (${a.get('total', 0):,.0f})" for a in analysis["anomalies"]])
    else:
        anomaly_lines = "  No significant day-over-day changes detected."
    
    # Build top states lines
    top_states_lines = "\n".join([f"  • <b>{s['state']}</b>: ${s['total']:,.0f} (STHD ${s.get('sthd', 0):,.0f}, SSTB ${s.get('sstb', 0):,.0f}, MASA ${s.get('masa', 0):,.0f})" for s in analysis.get("top_states", [])])
    
    # Day-over-day comparison if available
    day_over_day = ""
    if previous_data and previous_data.get("total_amount"):
        prev_total = previous_data["total_amount"]
        curr_total = analysis.get("total_amount", 0)
        change = curr_total - prev_total
        pct = (change / prev_total * 100) if prev_total else 0
        direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        day_over_day = f"""
📊 <b>DAY-OVER-DAY</b>
  Previous: ${prev_total:,.0f}
  Current:  ${curr_total:,.0f}
  {direction} Change: ${change:,.0f} ({pct:+.1f}%)"""
    
    report = f"""🏗️ <b>CAST REPORT — {date_str}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>DAILY EMBED INTELLIGENCE</b>
States tracked: {analysis.get('total_states', 0)}
Total volume: ${analysis.get('total_amount', 0):,.0f}
Total embeds: {analysis.get('total_count', 0):,}

📦 <b>BY MATERIAL CATEGORY:</b>
• STHD: ${analysis.get('sthd_total', 0):,.0f}
• SSTB: ${analysis.get('sstb_total', 0):,.0f}
• MASA: ${analysis.get('masa_total', 0):,.0f}
{day_over_day}

🚨 <b>ANOMALIES (>50% DAY-OVER-DAY)</b>
{anomaly_lines}

🏆 <b>TOP STATES BY VOLUME</b>
{top_states_lines}

━━━━━━━━━━━━━━━━━━━━
💡 <b>WHAT IS CAST REPORT?</b>
CAST tracks Simpson Strong-Tie embed sales across the United States — STHD, SSTB, and MASA categories — to identify construction momentum, state-level demand shifts, and supply-chain signals before they hit the headlines.

{get_cast_footer()}

━━━━━━━━━━━━━━━━━━━━
🏗️ <b>CONSTRUCTION MARKETS</b>
<a href="{CAST_LANDING_URL}">CAST Report</a> — 90-day construction intelligence."""
    
    return report


def get_cast_footer():
    """Standard footer for CAST Report"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>Get construction intelligence →</b>
<a href="{CAST_LANDING_URL}">CAST Report</a>
<b>Monthly Pulse — $799</b> | <b>Daily Brief — $1,899</b> | <b>Full Intelligence — $3,499</b>"""


# Integration helper: what CAST does NOT include
CAST_EXCLUDED_CONTENT = """
CAST Report EXCLUDES:
- Financial market data (goes to Overnight Edge)
- Stock prices, futures, VIX (goes to Overnight Edge)
- Prediction markets (goes to Overnight Edge)
- X/Twitter sentiment (goes to Overnight Edge)
"""
