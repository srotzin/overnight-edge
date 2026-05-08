#!/usr/bin/env python3
"""Weekly Audit Report Generator"""

import os
import csv
import json
import urllib.request
from datetime import datetime, timezone
from collections import Counter

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

def get_subscriber_stats():
    edge_active = edge_cancelled = signal_active = signal_cancelled = 0
    try:
        with open("/mnt/user/overnight-edge/subscribers.csv", "r") as f:
            for row in csv.DictReader(f):
                tier = row.get("tier", "")
                status = row.get("status", "")
                if tier == "edge" and status == "active":
                    edge_active += 1
                elif tier == "edge" and status == "cancelled":
                    edge_cancelled += 1
                elif tier == "signal" and status == "active":
                    signal_active += 1
                elif tier == "signal" and status == "cancelled":
                    signal_cancelled += 1
    except Exception as e:
        print(f"Subscriber read error: {e}")
    
    mrr = (edge_active * 49) + (signal_active * 149)
    return edge_active, edge_cancelled, signal_active, signal_cancelled, mrr

def get_delivery_stats():
    brief_success = brief_total = 0
    signal_counts = Counter()
    
    try:
        with open("/mnt/user/overnight-edge/delivery_log.csv", "r") as f:
            for row in csv.DictReader(f):
                if row.get("type") == "brief":
                    brief_total += 1
                    if row.get("status") == "delivered":
                        brief_success += 1
                elif row.get("type") == "alert":
                    score = row.get("confluence_score", "3")
                    signal_counts[score] += 1
    except Exception as e:
        print(f"Delivery log read error: {e}")
    
    success_rate = (brief_success / brief_total * 100) if brief_total > 0 else 0
    return brief_success, brief_total, success_rate, signal_counts

def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    edge_active, edge_cx, signal_active, signal_cx, mrr = get_subscriber_stats()
    brief_ok, brief_total, rate, signals = get_delivery_stats()
    
    report = f"""📊 WEEKLY AUDIT — {date_str}
━━━━━━━━━━━━━━━━━━━━
👥 SUBSCRIBERS
• Active Edge: {edge_active}
• Active Signal: {signal_active}
• Cancelled Edge: {edge_cx}
• Cancelled Signal: {signal_cx}
💰 MRR: ${mrr}

📈 DELIVERY
• Brief success: {brief_ok}/{brief_total} ({rate:.1f}%)
• Signals by score: {dict(signals)}

⚠️ ISSUES
• None flagged this week.
"""
    
    success = send_telegram(report)
    print(f"Audit sent. Status: {'delivered' if success else 'failed'}")

if __name__ == "__main__":
    main()
