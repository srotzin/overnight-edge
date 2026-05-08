#!/bin/bash
# Setup cron jobs for Overnight Edge services

# Remove old entries if they exist
crontab -l 2>/dev/null | grep -v "overnight-edge" | crontab -

# Add new entries
(crontab -l 2>/dev/null; cat <<'CRON'
# Overnight Edge - Daily Brief at 7:30 AM EST (12:30 UTC)
30 12 * * 1-5 cd /mnt/user/overnight-edge && python3 services/overnight_edge.py >> /mnt/user/overnight-edge/services/edge.log 2>&1

# SignalSynthesizer - Every 30 min during market hours (9:30 AM - 4:00 PM EST)
# 14:30-21:00 UTC, every 30 min, weekdays
*/30 14-20 * * 1-5 cd /mnt/user/overnight-edge && python3 services/signal_synthesizer.py >> /mnt/user/overnight-edge/services/signal.log 2>&1
0 21 * * 1-5 cd /mnt/user/overnight-edge && python3 services/signal_synthesizer.py >> /mnt/user/overnight-edge/services/signal.log 2>&1

# Weekly Audit - Sundays at 12:00 PM EST (17:00 UTC)
0 17 * * 0 cd /mnt/user/overnight-edge && python3 services/weekly_audit.py >> /mnt/user/overnight-edge/services/audit.log 2>&1
CRON
) | crontab -

echo "Cron jobs installed:"
crontab -l | grep overnight-edge
