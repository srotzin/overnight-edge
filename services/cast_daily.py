import os
import csv
import json
import urllib.request
import re
from datetime import datetime, timezone
import sys
import glob

# Import redesigned template
from cast_redesign import generate_cast_report, get_cast_footer, embed_context

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
ADMIN_CHAT = "5975342168"

CAST_INGEST_API = "https://pourpulse-v2-idy4zhor7-hivecivilization.vercel.app/api/embeds/ingest"
CAST_WEBHOOK_SECRET = os.environ.get("CAST_WEBHOOK_SECRET", "")
LANDING_URL = "https://castreport.com"

# CAST Report is a separate product — drives to castreport.com
# Unique voice: construction industry professional, supply-chain focused
# Content boundaries: ONLY construction data, embed tables, housing permits, lumber futures, Simpson Strong-Tie embed data
# NO equity market data, NO prediction markets, NO X sentiment

CAST_STRIPE_PRICES = {
    "monthly_pulse": "price_1TVDdEGrDuTtAB3meaYcvbs7",
    "daily_brief": "price_1TVDdcGrDuTtAB3mSV1cb9ok",
    "full_intelligence": "price_1TVDeEGrDuTtAB3m3EItsKrE",
    "signals": "price_1TVDrMGrDuTtAB3maPDuOQap",
    "forecast": "price_1TVDrrGrDuTtAB3mG2idzI3V",
    "vision": "price_1TVDsAGrDuTtAB3mJem4XcGr",
    "national": "price_1TVDsPGrDuTtAB3mTn82XBnI",
    "permitflow": "price_1TVDshGrDuTtAB3mKSDc6chZ",
}

CAST_STRIPE_SECRET = os.environ.get("CAST_STRIPE_SECRET", "")

def create_cast_checkout_url(price_id: str) -> str:
    """Create a Stripe Checkout session URL from a Price ID"""
    if not CAST_STRIPE_SECRET:
        return f"https://buy.stripe.com/{price_id}"
    try:
        import urllib.request
        url = "https://api.stripe.com/v1/checkout/sessions"
        data = urllib.parse.urlencode({
            "mode": "subscription",
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": 1,
            "success_url": "https://castreport.com/success",
            "cancel_url": "https://castreport.com",
        }).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Bearer {CAST_STRIPE_SECRET}",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        return result.get("url", "https://castreport.com")
    except Exception as e:
        print(f"Stripe checkout error: {e}")
        return "https://castreport.com"

def send_telegram(text: str, chat_id: str = ADMIN_CHAT):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram send failed to {chat_id}: {e}")
        return False

def log_delivery(date_str: str, dtype: str, count: int, status: str):
    os.makedirs("/mnt/user/castreport", exist_ok=True)
    with open("/mnt/user/castreport/delivery_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, dtype, count, status])

def get_latest_embed_file():
    files = glob.glob("/mnt/user/castreport/embeds/*.xlsx")
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return latest

def get_previous_embed_file(latest_file):
    """Get the second most recent embed file for day-over-day comparison"""
    files = glob.glob("/mnt/user/castreport/embeds/*.xlsx")
    if len(files) < 2:
        return None
    # Sort by modification time, descending
    files_sorted = sorted(files, key=os.path.getmtime, reverse=True)
    if files_sorted[0] == latest_file:
        return files_sorted[1] if len(files_sorted) > 1 else None
    return files_sorted[0]

def parse_embed_excel(filepath: str) -> dict:
    """Parse Simpson Strong-Tie embed Excel file directly"""
    if not HAS_PANDAS:
        print("Pandas not available, falling back to ingest API")
        return None
    try:
        import pandas as pd
        df = pd.read_excel(filepath, sheet_name='US Sales BI Report', header=None)
        
        # Skip first 2 rows (date row + header row)
        data = df.iloc[2:].copy()
        data.columns = ['Shipping_Region', 'Shipping_Country', 'Material', 'Invoice_Amount', 'Material_Category']
        
        # Remove header/footer rows
        data = data[data['Shipping_Region'] != 'Shipping Region']
        data = data[data['Shipping_Region'].notna()]
        data = data[data['Material'] != 'Material']
        
        # Convert amounts to numeric
        data['Invoice_Amount'] = pd.to_numeric(data['Invoice_Amount'], errors='coerce')
        data = data[data['Invoice_Amount'].notna()]
        
        # Clean material category
        data['Material_Category'] = data['Material_Category'].fillna(data['Material'].apply(
            lambda x: 'STHD' if str(x).startswith('STHD') else 
                      'SSTB' if str(x).startswith('SSTB') else
                      'MASA' if str(x).startswith('MASA') else 'OTHER'
        ))
        
        # Aggregate by state and category
        state_data = []
        for state in sorted(data['Shipping_Region'].unique()):
            state_df = data[data['Shipping_Region'] == state]
            sthd = state_df[state_df['Material_Category'] == 'STHD']['Invoice_Amount'].sum()
            sstb = state_df[state_df['Material_Category'] == 'SSTB']['Invoice_Amount'].sum()
            masa = state_df[state_df['Material_Category'] == 'MASA']['Invoice_Amount'].sum()
            total = state_df['Invoice_Amount'].sum()
            count = len(state_df)
            
            state_data.append({
                "state": state,
                "sthd": round(float(sthd), 2),
                "sstb": round(float(sstb), 2),
                "masa": round(float(masa), 2),
                "total": round(float(total), 2),
                "count": int(count),
            })
        
        total_amount = float(data['Invoice_Amount'].sum())
        total_count = len(data)
        
        return {
            "states": state_data,
            "summary": {
                "total_amount": round(total_amount, 2),
                "total_count": total_count,
                "total_states": len(state_data),
                "sthd_total": round(float(data[data['Material_Category'] == 'STHD']['Invoice_Amount'].sum()), 2),
                "sstb_total": round(float(data[data['Material_Category'] == 'SSTB']['Invoice_Amount'].sum()), 2),
                "masa_total": round(float(data[data['Material_Category'] == 'MASA']['Invoice_Amount'].sum()), 2),
            }
        }
    except Exception as e:
        print(f"Direct parse failed: {e}")
        return None

def ingest_embeds(filepath: str) -> dict:
    # First try direct parsing
    direct_data = parse_embed_excel(filepath)
    if direct_data:
        print(f"Direct parse successful: {direct_data['summary']['total_amount']}")
        return {"success": True, "data": direct_data}
    
    # Fallback to API
    try:
        with open(filepath, "rb") as f:
            file_data = f.read()
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = []
        body.append(f"--{boundary}".encode())
        body.append(b'Content-Disposition: form-data; name="file"')
        body.append(b"")
        body.append(file_data)
        body.append(f"--{boundary}--".encode())
        payload = b"\r\n".join(body)
        req = urllib.request.Request(CAST_INGEST_API, data=payload, headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Webhook-Secret": CAST_WEBHOOK_SECRET,
        })
        response = urllib.request.urlopen(req, timeout=60)
        result = json.loads(response.read().decode())
        return {"success": True, "data": result}
    except Exception as e:
        print(f"Ingest failed: {e}")
        return {"success": False, "error": str(e)}

def analyze_data(data: dict, previous_data: dict = None) -> dict:
    anomalies = []
    state_summary = []
    states = data.get("states", [])
    
    # Build previous day lookup if available
    prev_lookup = {}
    if previous_data and "states" in previous_data:
        for s in previous_data["states"]:
            prev_lookup[s.get("state", "")] = s.get("total", 0)
    
    for state in states:
        name = state.get("state", "Unknown")
        sthd = state.get("sthd", 0)
        sstb = state.get("sstb", 0)
        masa = state.get("masa", 0)
        total = state.get("total", 0)
        
        # Calculate day-over-day change if previous data exists
        change = 0
        if name in prev_lookup and prev_lookup[name] > 0:
            change = (total - prev_lookup[name]) / prev_lookup[name]
        
        if abs(change) > 0.5:
            direction = "📈 SURGE" if change > 0 else "📉 DROP"
            anomalies.append({
                "state": name,
                "change": f"{change:+.1%}",
                "direction": direction,
                "sthd": sthd,
                "sstb": sstb,
                "masa": masa,
                "total": total,
            })
        
        state_summary.append({
            "state": name,
            "total": total,
            "sthd": sthd,
            "sstb": sstb,
            "masa": masa,
        })
    
    top_states = sorted(state_summary, key=lambda x: x["total"], reverse=True)[:5]
    
    summary = data.get("summary", {})
    
    return {
        "anomalies": anomalies,
        "top_states": top_states,
        "total_states": len(states),
        "total_amount": summary.get("total_amount", 0),
        "total_count": summary.get("total_count", 0),
        "sthd_total": summary.get("sthd_total", 0),
        "sstb_total": summary.get("sstb_total", 0),
        "masa_total": summary.get("masa_total", 0),
    }

def generate_subscription_footer():
    return f"""━━━━━━━━━━━━━━━━━━━━
🏗️ <b>SUBSCRIBE TO CAST REPORT</b>

<a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""

def generate_cast_alert(analysis: dict) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    if analysis["anomalies"]:
        anomaly_lines = [f"{a['direction']} <b>{a['state']}</b>: {a['change']} (${a['total']:,.0f})" for a in analysis["anomalies"]]
        anomaly_text = "\n".join(anomaly_lines)
    else:
        anomaly_text = "No significant day-over-day changes detected."
    
    top_states_text = "\n".join([f"• <b>{s['state']}</b>: ${s['total']:,.0f} (STHD ${s['sthd']:,.0f}, SSTB ${s['sstb']:,.0f}, MASA ${s['masa']:,.0f})" for s in analysis["top_states"]])
    
    subscription = generate_subscription_footer()
    
    return f"""🏗️ <b>CAST REPORT — {date_str}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>DAILY EMBED INTELLIGENCE</b>
States tracked: {analysis['total_states']}
Total volume: ${analysis['total_amount']:,.0f}
Total embeds: {analysis['total_count']:,}

📦 <b>BY MATERIAL:</b>
• STHD: ${analysis['sthd_total']:,.0f}
• SSTB: ${analysis['sstb_total']:,.0f}
• MASA: ${analysis['masa_total']:,.0f}

🚨 <b>ANOMALIES (>50% day-over-day)</b>
{anomaly_text}

🏆 <b>TOP STATES</b>
{top_states_text}

{subscription}

⬇️ <b>CONSTRUCTION MARKETS</b>
<a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""

def generate_delayed_notice() -> str:
    return f"""⏰ <b>CAST REPORT — DATA DELAYED</b>
━━━━━━━━━━━━━━━━━━━━

The daily Simpson Strong-Tie embed file has not arrived.

Expected: 6:00 AM ET
Status: DELAYED

The alert will auto-resend when data becomes available.

⬇️ <a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""

def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    embed_file = get_latest_embed_file()
    if not embed_file:
        notice = generate_delayed_notice()
        sent = send_telegram(notice)
        log_delivery(date_str, "delayed_notice", 1, "delivered" if sent else "failed")
        print(f"Data delayed notice sent: {'OK' if sent else 'FAIL'}")
        return
    
    print(f"Found embed file: {embed_file}")
    
    # Get previous file for comparison
    prev_file = get_previous_embed_file(embed_file)
    previous_data = None
    if prev_file:
        print(f"Previous file for comparison: {prev_file}")
        prev_result = ingest_embeds(prev_file)
        if prev_result["success"]:
            previous_data = prev_result["data"]
    
    result = ingest_embeds(embed_file)
    if not result["success"]:
        error_msg = f"CAST ingest failed: {result.get('error', 'Unknown error')}"
        print(error_msg)
        send_telegram(f"⚠️ <b>CAST SYSTEM ALERT</b>\n{error_msg}")
        log_delivery(date_str, "ingest", 0, "failed")
        return
    
    analysis = analyze_data(result["data"], previous_data)
    alert = generate_cast_alert(analysis)
    sent = send_telegram(alert)
    log_delivery(date_str, "daily_alert", 1, "delivered" if sent else "failed")
    print(f"CAST alert sent: {'OK' if sent else 'FAIL'}")
    
    if analysis["anomalies"]:
        highlight = f"""🚨 <b>CAST ANOMALY ALERT</b>
━━━━━━━━━━━━━━━━━━━━
{len(analysis['anomalies'])} state(s) showing >50% day-over-day change.

Top anomaly:
{analysis['anomalies'][0]['direction']} <b>{analysis['anomalies'][0]['state']}</b>: {analysis['anomalies'][0]['change']}

Full details in the daily brief above.

⬇️ <a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""
        send_telegram(highlight)

if __name__ == "__main__":
    main()
