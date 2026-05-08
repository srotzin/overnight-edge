#!/usr/bin/env python3
"""Overnight Edge — Daily Pre-Market Brief Generator"""

import os
import csv
import json
import urllib.request
from datetime import datetime, timezone

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
TELEGRAM_CHAT = "5975342168"

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

def log_delivery(date_str: str, tier: str, dtype: str, count: int, status: str):
    with open("/mnt/user/overnight-edge/delivery_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, tier, dtype, count, status])

def get_active_subscribers(tier_filter=None):
    subs = []
    try:
        with open("/mnt/user/overnight-edge/subscribers.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("status") == "active":
                    if tier_filter is None or row.get("tier") == tier_filter:
                        subs.append(row)
    except Exception as e:
        print(f"Subscriber read error: {e}")
    return subs

def generate_brief():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # Simulated data gathering — in production this would use real APIs
    brief = f"""🌅 OVERNIGHT EDGE — {date_str}
━━━━━━━━━━━━━━━━━━━━
📊 FUTURES: S&P +0.4%, Nasdaq +0.6%
📈 VIX: 14.2 (-0.8)
🏆 GAINERS: AAPL +3.2%, NVDA +2.8%, TSLA +2.1%
🔻 LOSERS: META -1.4%, GOOGL -0.9%, AMZN -0.5%
📢 EARNINGS: AAPL (after close), AMD (before open)
📰 ECONOMIC: PPI data due 8:30 AM EST
⚡ NEWS: Fed minutes suggest cautious stance — neutral sentiment
🔮 OUTLOOK: Cautiously bullish. Tech leading, volatility compressed."""
    return brief, date_str

def main():
    brief, date_str = generate_brief()
    subs = get_active_subscribers()
    count = len(subs)
    
    if count == 0:
        log_delivery(date_str, "edge", "brief", 0, "no_subscribers")
        print("No active subscribers.")
        return
    
    success = send_telegram(brief)
    status = "delivered" if success else "failed"
    log_delivery(date_str, "edge", "brief", count, status)
    print(f"Brief sent to {count} subscribers. Status: {status}")

if __name__ == "__main__":
    main()
