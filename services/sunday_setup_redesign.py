"""
REDESIGNED THE SUNDAY SETUP REPORT
==================================
Unique voice: Editorial, strategic, week-ahead focused — like a Barron's cover story
Purpose: FREE marketing piece that converts readers to paid subscribers
Content: Economic calendar, earnings, geopolitical risk, options expiration, XSignal synthesis
Includes: "THIS WEEK ON OVERNIGHT EDGE" section teasing each paid tier
"""

from datetime import datetime, timezone, timedelta

LANDING_URL = "https://overnight-edge.vercel.app"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_bot.png"

# Product Buy Button IDs for CTAs
DD_BUY = "buy_btn_1TWLs4GrDuTtAB3mRdCm5bnZ"
SS_BUY = "buy_btn_1TWLrSGrDuTtAB3muePQIrWx"
SQR_BUY = "buy_btn_1TWLniGrDuTtAB3mojv83V6D"
X10_BUY = "buy_btn_1TWLqtGrDuTtAB3m9vVOxud8"
X20_BUY = "buy_btn_1TWLqAGrDuTtAB3mBu2MrOMW"
PC_BUY = "buy_btn_1TWLpXGrDuTtAB3mzRewSdxs"
PP_BUY = "buy_btn_1TWLouGrDuTtAB3mhwdzodZK"


def generate_sunday_setup_report(week_of, economic_calendar, top_earnings, geopolitical, options_exp, signals_syn, week_outlook):
    """
    Generate The Sunday Setup — the free weekly marketing piece
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Build calendar lines
    cal_lines = "\n".join([f"  <b>{e['day']}:</b> {e['event']} {e['time']}" + (f" | Consensus: {e['consensus']}" if e.get('consensus') else "") for e in economic_calendar]) if economic_calendar else "  No major events scheduled."
    
    # Build earnings lines
    earn_lines = "\n".join([f"  <b>{e['ticker']}:</b> EPS est ${e.get('eps_consensus', 'N/A')} | Rev {e.get('rev_consensus', 'N/A')}" for e in top_earnings]) if top_earnings else "  No major earnings this week."
    
    # Teaser section — THIS WEEK ON OVERNIGHT EDGE
    teasers = f"""━━━━━━━━━━━━━━━━━━━━
<b>📡 THIS WEEK ON OVERNIGHT EDGE</b>

Every trading day, our subscribers get:

<b>🌅 Daily Digest ($49)</b>
Pre-market brief at 8:00 AM EST. Futures, VIX, movers, overnight news, earnings, economic data. The edge before the bell.
→ <a href="{LANDING_URL}">Get Daily Digest</a>

<b>🦈 Signal Synthesizer ($149)</b>
Congressional trades (STOCK Act), SEC Form 4 insider filings, unusual options flow, dark pool prints. Follow the smart money.
→ <a href="{LANDING_URL}">Get Signal Synthesizer</a>

<b>🚨 Short Squeeze Radar ($99)</b>
Twice-daily scans for squeeze mechanics: short interest, float, days to cover, gamma ramp, borrow utilization. Score 6+ alerts.
→ <a href="{LANDING_URL}">Get Short Squeeze Radar</a>

<b>📡 X10 Signal ($249)</b>
Real-time intelligence from 20 top trading accounts on X. Keyword confluence across equities, commodities, FX, derivatives.
→ <a href="{LANDING_URL}">Get X10 Signal</a>

<b>🌐 X20 Signal ($449)</b>
Full-spectrum X scanning, cross-asset correlation, instant 4+ confluence alerts. Includes Short Squeeze Radar.
→ <a href="{LANDING_URL}">Get X20 Signal</a>

<b>🔮 PredictionCore ($299)</b>
Daily prediction market tracking: Polymarket, Kalshi, consensus vs reality. The crowd is often wrong.
→ <a href="{LANDING_URL}">Get PredictionCore</a>

<b>🚨 Prediction Pro ($499)</b>
Instant shift alerts (>5% moves), new market detection, X sentiment divergence. For traders who need speed.
→ <a href="{LANDING_URL}">Get Prediction Pro</a>"""
    
    report = f"""📅 <b>THE SUNDAY SETUP — WEEK OF {week_of}</b>
━━━━━━━━━━━━━━━━━━━━
📅 {date_str} | Your weekly strategic briefing

<b>📆 ECONOMIC CALENDAR</b>
{cal_lines}

━━━━━━━━━━━━━━━━━━━━
<b>🏆 TOP EARNINGS</b>
{earn_lines}

━━━━━━━━━━━━━━━━━━━━
<b>🌍 GEOPOLITICAL WATCH</b>
{geopolitical}

━━━━━━━━━━━━━━━━━━━━
<b>📊 OPTIONS EXPIRATION</b>
{options_exp}

━━━━━━━━━━━━━━━━━━━━
<b>🔮 WHAT THE SIGNALS SAY</b>
{signals_syn}

━━━━━━━━━━━━━━━━━━━━
<b>📈 WEEK AHEAD OUTLOOK</b>
{week_outlook}

{teasers}

━━━━━━━━━━━━━━━━━━━━
<b>Get real-time alerts all week →</b>
<a href="{LANDING_URL}">overnight-edge.vercel.app</a>

⚠️ NOT FINANCIAL ADVICE"""
    
    return report


def get_sunday_setup_footer():
    """Standard footer for Sunday Setup"""
    return f"""━━━━━━━━━━━━━━━━━━━━
<b>The Sunday Setup is FREE every week.</b>
<b>Get real-time alerts →</b> <a href="{LANDING_URL}">overnight-edge.vercel.app</a>
<b>Subscribe to any tier →</b> <a href="{LANDING_URL}">View Pricing</a>"""
