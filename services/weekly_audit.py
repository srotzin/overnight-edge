import os
import csv
from datetime import datetime, timezone, timedelta
import urllib.request
import json

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
ADMIN_CHAT = "5975342168"
LOGO_PATH = "/mnt/user/overnight-edge/public/cartoons/overnight_logo_bot.png"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": ADMIN_CHAT, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Send failed: {e}")
        return False

def send_telegram_photo(photo_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    with open(photo_path, "rb") as f:
        photo_data = f.read()
    body = []
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="chat_id"')
    body.append(b"")
    body.append(ADMIN_CHAT.encode())
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="caption"')
    body.append(b"")
    body.append(caption.encode())
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="parse_mode"')
    body.append(b"")
    body.append(b"HTML")
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="photo"; filename="{os.path.basename(photo_path)}"'.encode())
    body.append(b"Content-Type: image/png")
    body.append(b"")
    body.append(photo_data)
    body.append(f"--{boundary}--".encode())
    payload = b"\r\n".join(body)
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Photo send failed: {e}")
        return False

def count_subscribers():
    tiers = {"digest": 0, "signal": 0, "squeeze": 0, "x10": 0, "x20": 0, "pulse-core": 0, "pulse-pro": 0, "sunday": 0}
    cancelled = 0
    try:
        with open("/mnt/user/overnight-edge/subscribers.csv", "r") as f:
            for row in csv.DictReader(f):
                tier = row.get("tier", "")
                status = row.get("status", "")
                if status == "active" and tier in tiers:
                    tiers[tier] += 1
                elif status == "cancelled":
                    cancelled += 1
                # Count addons
                if row.get("squeeze") == "active":
                    tiers["squeeze"] += 1
                if row.get("sunday") == "active":
                    tiers["sunday"] += 1
    except:
        pass
    return tiers, cancelled

def count_signals():
    score_counts = {"3": 0, "4": 0, "5": 0}
    total = 0
    try:
        with open("/mnt/user/overnight-edge/signal_accuracy.csv", "r") as f:
            for row in csv.DictReader(f):
                score = row.get("confluence_score", "")
                if score in score_counts:
                    score_counts[score] += 1
                    total += 1
    except:
        pass
    return score_counts, total

def count_xsignals():
    total = 0
    top_accounts = {}
    try:
        with open("/mnt/user/overnight-edge/xsignal_log.csv", "r") as f:
            for row in csv.DictReader(f):
                total += 1
                accounts = row.get("accounts_triggering", "").split(", ")
                for a in accounts:
                    top_accounts[a] = top_accounts.get(a, 0) + 1
    except:
        pass
    top_5 = sorted(top_accounts.items(), key=lambda x: x[1], reverse=True)[:5]
    return total, top_5

def count_predictions():
    divergences = 0
    total = 0
    try:
        with open("/mnt/user/overnight-edge/prediction_log.csv", "r") as f:
            for row in csv.DictReader(f):
                total += 1
                if row.get("divergence_flag", "") == "YES":
                    divergences += 1
    except:
        pass
    return total, divergences

def count_squeezes():
    total = 0
    high_score = 0
    try:
        with open("/mnt/user/overnight-edge/squeeze_log.csv", "r") as f:
            for row in csv.DictReader(f):
                total += 1
                score = int(row.get("squeeze_score", 0) or 0)
                if score >= 8:
                    high_score += 1
    except:
        pass
    return total, high_score

def count_deliveries():
    total_briefs = 0
    total_alerts = 0
    failed = 0
    try:
        with open("/mnt/user/overnight-edge/delivery_log.csv", "r") as f:
            for row in csv.DictReader(f):
                dtype = row.get("type", "")
                status = row.get("status", "")
                if "brief" in dtype:
                    total_briefs += 1
                elif "alert" in dtype:
                    total_alerts += 1
                if status != "delivered":
                    failed += 1
    except:
        pass
    return total_briefs, total_alerts, failed

def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    tiers, cancelled = count_subscribers()
    score_counts, signal_total = count_signals()
    x_total, x_top = count_xsignals()
    pred_total, pred_div = count_predictions()
    sq_total, sq_high = count_squeezes()
    briefs, alerts, failed = count_deliveries()
    
    mrr = (
        tiers["digest"] * 49 +
        tiers["signal"] * 149 +
        tiers["squeeze"] * 99 +
        tiers["x10"] * 249 +
        tiers["x20"] * 449 +
        tiers["pulse-core"] * 299 +
        tiers["pulse-pro"] * 499 +
        tiers["sunday"] * 29
    )
    
    x_top_text = "\n".join([f"• @{a}: {c} alerts" for a, c in x_top]) if x_top else "• No XSignal data yet"
    
    report = f"""📊 <b>WEEKLY AUDIT — {date_str}</b>
━━━━━━━━━━━━━━━━━━━━

<b>SUBSCRIBERS:</b>
• Daily Digest ($49): {tiers['digest']}
• Signal ($149): {tiers['signal']}
• Squeeze Radar ($99): {tiers['squeeze']}
• X10 ($249): {tiers['x10']}
• X20 ($449): {tiers['x20']}
• PredictionCore ($299): {tiers['pulse-core']}
• Prediction Pro ($499): {tiers['pulse-pro']}
• Sunday Setup ($29): {tiers['sunday']}
• Cancelled: {cancelled}
• <b>Total MRR: ${mrr}/mo</b>

<b>SIGNALS SENT:</b>
• Score 3 (Strong): {score_counts['3']}
• Score 4 (Very Strong): {score_counts['4']}
• Score 5 (Extreme): {score_counts['5']}
• Signal Total: {signal_total}

<b>XSIGNAL PERFORMANCE:</b>
• Total Alerts: {x_total}
• Top Accounts:
{x_top_text}

<b>SHORT SQUEEZE RADAR:</b>
• Total Scans: {sq_total}
• High Score (8+): {sq_high}

<b>PREDICTIONPULSE:</b>
• Total Reports: {pred_total}
• Divergences Flagged: {pred_div}

<b>DELIVERY:</b>
• Briefs: {briefs}
• Alerts: {alerts}
• Failed: {failed}
• Success Rate: {(briefs+alerts)/(briefs+alerts+failed)*100:.1f}% if (briefs+alerts+failed) > 0 else "N/A"

⚠️ Automated by KimiClaw AI. Not financial advice."""
    
    send_telegram_photo(LOGO_PATH, report)
    print("Weekly audit sent")

if __name__ == "__main__":
    main()
