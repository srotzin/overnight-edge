#!/usr/bin/env python3
"""Subscriber management helper"""

import sys
import csv
import os
from datetime import datetime, timezone

SUBSCRIBERS_CSV = "/mnt/user/overnight-edge/subscribers.csv"

def add_subscriber(email, tier):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(SUBSCRIBERS_CSV, "a", newline="") as f:
        csv.writer(f).writerow([email, tier, "active", now, ""])
    print(f"Added: {email} | {tier}")

def cancel_subscriber(email):
    rows = []
    found = False
    try:
        with open(SUBSCRIBERS_CSV, "r") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row.get("email") == email:
                    row["status"] = "cancelled"
                    found = True
                rows.append(row)
    except FileNotFoundError:
        print("No subscribers file found.")
        return
    
    if found:
        with open(SUBSCRIBERS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Cancelled: {email}")
    else:
        print(f"Not found: {email}")

def list_subscribers():
    try:
        with open(SUBSCRIBERS_CSV, "r") as f:
            for row in csv.DictReader(f):
                print(f"{row['email']} | {row['tier']} | {row['status']} | {row['start_date']}")
    except FileNotFoundError:
        print("No subscribers yet.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python subscribers.py [add|cancel|list] [email] [tier]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 4:
        add_subscriber(sys.argv[2], sys.argv[3])
    elif cmd == "cancel" and len(sys.argv) >= 3:
        cancel_subscriber(sys.argv[2])
    elif cmd == "list":
        list_subscribers()
    else:
        print("Usage: python subscribers.py [add|cancel|list] [email] [tier]")
