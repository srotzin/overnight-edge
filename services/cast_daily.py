import os
import csv
import json
import urllib.request
import re
from datetime import datetime, timezone
import sys
import glob

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
ADMIN_CHAT = "5975342168"

CAST_INGEST_API = "https://pourpulse-v2-idy4zhor7-hivecivilization.vercel.app/api/embeds/ingest"
CAST_WEBHOOK_SECRET = os.environ.get("CAST_WEBHOOK_SECRET", "")
LANDING_URL = "https://castreport.com"

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
        # Fallback: direct payment link format (won't work without secret)
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
    with open("/mnt/user/castreport/delivery_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, dtype, count, status])

def get_latest_embed_file():
    files = glob.glob("/mnt/user/castreport/embeds/*.xlsx")
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return latest

def ingest_embeds(filepath: str) -> dict:
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

def analyze_data(data: dict) -> dict:
    anomalies = []
    state_summary = []
    states = data.get("data", {}).get("states", [])
    for state in states:
        name = state.get("state", "Unknown")
        sthd = state.get("sthd", 0)
        sstb = state.get("sstb", 0)
        masa = state.get("masa", 0)
        change = state.get("day_over_day_change", 0)
        if abs(change) > 0.5:
            direction = "📈 SURGE" if change > 0 else "📉 DROP"
            anomalies.append({
                "state": name,
                "change": f"{change:+.1%}",
                "direction": direction,
                "sthd": sthd,
                "sstb": sstb,
                "masa": masa,
            })
        state_summary.append({
            "state": name,
            "total": sthd + sstb + masa,
        })
    top_states = sorted(state_summary, key=lambda x: x["total"], reverse=True)[:5]
    return {
        "anomalies": anomalies,
        "top_states": top_states,
        "total_states": len(states),
    }

def generate_subscription_footer():
    # TODO: Replace with actual Stripe Payment Link URLs once created in dashboard
    # Price IDs are backend identifiers, not clickable URLs
    return f"""━━━━━━━━━━━━━━━━━━━━
🏗️ <b>SUBSCRIBE TO CAST REPORT</b>

<a href="https://castreport.com">CAST Report</a> — 90-day construction intelligence."""

def generate_cast_alert(analysis: dict) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    if analysis["anomalies"]:
        anomaly_lines = [f"{a['direction']} <b>{a['state']}</b>: {a['change']}" for a in analysis["anomalies"]]
        anomaly_text = "\n".join(anomaly_lines)
    else:
        anomaly_text = "No anomalies detected."
    top_states_text = "\n".join([f"• <b>{s['state']}</b>: {s['total']:,} embeds" for s in analysis["top_states"]])
    subscription = generate_subscription_footer()
    return f"""🏗️ <b>CAST REPORT — {date_str}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>DAILY EMBED INTELLIGENCE</b>
States tracked: {analysis['total_states']}

🚨 <b>ANOMALIES</b>
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
    result = ingest_embeds(embed_file)
    if not result["success"]:
        error_msg = f"CAST ingest failed: {result.get('error', 'Unknown error')}"
        print(error_msg)
        send_telegram(f"⚠️ <b>CAST SYSTEM ALERT</b>\n{error_msg}")
        log_delivery(date_str, "ingest", 0, "failed")
        return
    analysis = analyze_data(result["data"])
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
