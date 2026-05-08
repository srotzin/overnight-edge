#!/bin/bash
# Overnight Edge — Complete 6-Service Cron Setup

CRON_FILE=$(mktemp)

# 1. Daily Digest — 7:30 AM EST (11:30 UTC)
echo "30 11 * * 1-5 cd /mnt/user/overnight-edge && python3 services/overnight_edge.py >> /mnt/user/overnight-edge/services/edge.log 2>&1" >> "$CRON_FILE"

# 2. EDGAR Monitor — every 15 min during market hours (14:00-21:00 UTC, Mon-Fri)
echo "*/15 14-21 * * 1-5 cd /mnt/user/overnight-edge && python3 services/edgar_monitor.py >> /mnt/user/overnight-edge/services/edgar.log 2>&1" >> "$CRON_FILE"

# 3. Signal Synthesizer — every 30 min during market hours + 21:00 UTC close
echo "*/30 14-20 * * 1-5 cd /mnt/user/overnight-edge && python3 services/signal_synthesizer.py >> /mnt/user/overnight-edge/services/signal.log 2>&1" >> "$CRON_FILE"
echo "0 21 * * 1-5 cd /mnt/user/overnight-edge && python3 services/signal_synthesizer.py >> /mnt/user/overnight-edge/services/signal.log 2>&1" >> "$CRON_FILE"

# 4. X10 Signal — every 30 min during market hours
echo "*/30 14-20 * * 1-5 cd /mnt/user/overnight-edge && python3 services/xsignal_basic.py >> /mnt/user/overnight-edge/services/x10.log 2>&1" >> "$CRON_FILE"

# 5. X20 Signal — every 15 min during market hours + EOD synthesis at 21:30 UTC (4:30 PM EST)
echo "*/15 14-20 * * 1-5 cd /mnt/user/overnight-edge && python3 services/xsignal_pro.py >> /mnt/user/overnight-edge/services/x20.log 2>&1" >> "$CRON_FILE"
echo "30 21 * * 1-5 cd /mnt/user/overnight-edge && python3 services/xsignal_pro.py >> /mnt/user/overnight-edge/services/x20.log 2>&1" >> "$CRON_FILE"

# 6. PredictionCore — 4x daily: 8 AM, 12 PM, 4 PM, 8 PM EST (12:00, 16:00, 20:00, 00:00 UTC)
echo "0 12,16,20,0 * * * cd /mnt/user/overnight-edge && python3 services/prediction_core.py >> /mnt/user/overnight-edge/services/pulse.log 2>&1" >> "$CRON_FILE"

# 7. Prediction Pro — every 30 min during active hours (12:00-01:00 UTC) + EOD at 23:00 UTC
echo "*/30 12-23 * * * cd /mnt/user/overnight-edge && python3 services/prediction_pro.py >> /mnt/user/overnight-edge/services/pro.log 2>&1" >> "$CRON_FILE"
echo "0 0-1 * * * cd /mnt/user/overnight-edge && python3 services/prediction_pro.py >> /mnt/user/overnight-edge/services/pro.log 2>&1" >> "$CRON_FILE"
echo "0 23 * * * cd /mnt/user/overnight-edge && python3 services/prediction_pro.py >> /mnt/user/overnight-edge/services/pro.log 2>&1" >> "$CRON_FILE"

# 8. Weekly Audit — Sundays 12 PM EST (16:00 UTC)
echo "0 16 * * 0 cd /mnt/user/overnight-edge && python3 services/weekly_audit.py >> /mnt/user/overnight-edge/services/audit.log 2>&1" >> "$CRON_FILE"

# Install
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "All 6 services cron jobs installed:"
crontab -l | grep overnight-edge
