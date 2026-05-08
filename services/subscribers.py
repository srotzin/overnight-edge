import csv
import sys
from datetime import datetime, timezone

SUBSCRIBERS_FILE = "/mnt/user/overnight-edge/subscribers.csv"

def load_subscribers():
    subs = []
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            for row in csv.DictReader(f):
                subs.append(row)
    except:
        pass
    return subs

def save_subscribers(subs):
    if not subs:
        return
    fieldnames = list(subs[0].keys())
    with open(SUBSCRIBERS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(subs)

def add_subscriber(email, tier, telegram_id=""):
    subs = load_subscribers()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Check if exists
    for sub in subs:
        if sub.get("email") == email:
            # Update tier
            sub["tier"] = tier
            sub["status"] = "active"
            sub["joined_date"] = now
            if telegram_id:
                sub["telegram_id"] = telegram_id
            save_subscribers(subs)
            print(f"Updated: {email} → {tier} (active)")
            return
    
    # New subscriber
    new_sub = {
        "email": email,
        "telegram_id": telegram_id,
        "tier": tier,
        "status": "active",
        "joined_date": now,
        "squeeze": "cancelled",
        "sunday": "cancelled",
    }
    subs.append(new_sub)
    save_subscribers(subs)
    print(f"Added: {email} → {tier}")

def add_addon(email, addon):
    """Add squeeze or sunday addon to existing subscriber"""
    subs = load_subscribers()
    for sub in subs:
        if sub.get("email") == email:
            if addon in ["squeeze", "sunday"]:
                sub[addon] = "active"
                save_subscribers(subs)
                print(f"Added addon: {email} → {addon}")
                return
    print(f"Subscriber not found: {email}")

def cancel_subscriber(email):
    subs = load_subscribers()
    found = False
    for sub in subs:
        if sub.get("email") == email:
            sub["status"] = "cancelled"
            sub["squeeze"] = "cancelled"
            sub["sunday"] = "cancelled"
            found = True
    if found:
        save_subscribers(subs)
        print(f"Cancelled: {email} (all tiers)")
    else:
        print(f"Not found: {email}")

def list_subscribers():
    subs = load_subscribers()
    tiers = {"digest": 0, "signal": 0, "x10": 0, "x20": 0, "pulse-core": 0, "pulse-pro": 0, "squeeze": 0, "sunday": 0}
    for sub in subs:
        if sub.get("status") == "active":
            tier = sub.get("tier", "")
            if tier in tiers:
                tiers[tier] += 1
        # Count addons separately
        if sub.get("squeeze") == "active":
            tiers["squeeze"] += 1
        if sub.get("sunday") == "active":
            tiers["sunday"] += 1
    for tier, count in tiers.items():
        print(f"  {tier}: {count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 subscribers.py add email@x.com tier [telegram_id]")
        print("  python3 subscribers.py addon email@x.com squeeze|sunday")
        print("  python3 subscribers.py cancel email@x.com")
        print("  python3 subscribers.py list")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 4:
        add_subscriber(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "addon" and len(sys.argv) == 4:
        add_addon(sys.argv[2], sys.argv[3])
    elif cmd == "cancel" and len(sys.argv) == 3:
        cancel_subscriber(sys.argv[2])
    elif cmd == "list":
        list_subscribers()
    else:
        print("Invalid command")
