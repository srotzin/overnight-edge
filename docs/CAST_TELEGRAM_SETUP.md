# CAST Report — Telegram Bot Setup

CAST Report now supports its **own** Telegram bot, separate from Overnight Edge.

## Why Separate?

- **Different audience**: Construction professionals ≠ equity traders
- **Different content**: Embed data, permits, lumber — not futures or options
- **Different product**: CAST is a standalone brand at castreport.com

## Setup Steps

### 1. Create a New Bot via BotFather

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Name it: `CAST Report`
4. Username: `castreport_bot` (or similar — must end in `_bot`)
5. Copy the **token** (looks like `123456789:ABC...`)

### 2. Create a Channel for Public Posts

1. In Telegram, create a new channel: **CAST Report Alerts**
2. Set username: `@castreport_alerts`
3. Add your new bot as an **administrator**
4. Copy the **channel ID** (you'll get this from a test message)

### 3. Set Environment Variables

Add to your server environment (or `.env` file):

```bash
export CAST_TELEGRAM_TOKEN="your_new_bot_token_here"
export CAST_ADMIN_CHAT="your_admin_chat_id"
export CAST_PUBLIC_CHANNEL="your_channel_id_here"
```

### 4. Get Channel/Chat IDs

Run this quick test:

```python
import os, json, urllib.request
TOKEN = os.environ.get("CAST_TELEGRAM_TOKEN")
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resp = urllib.request.urlopen(url)
print(json.loads(resp.read()))
```

Send a message to your bot/channel first, then run the script.

## Fallback Behavior

If `CAST_TELEGRAM_TOKEN` is **not set**, the code falls back to the Overnight Edge bot. This lets you migrate gradually.

## Architecture

| Variable | Purpose | Example |
|---|---|---|
| `CAST_TELEGRAM_TOKEN` | Bot token for CAST | `123456:ABC...` |
| `CAST_ADMIN_CHAT` | Admin notifications | `5975342168` |
| `CAST_PUBLIC_CHANNEL` | Public channel posts | `-1001234567890` |

## Code Location

The setup lives in:
- `/mnt/user/overnight-edge/services/cast_daily.py` (lines 16–26)
- Uses `os.environ.get()` with fallback to Overnight Edge defaults

---

**Done.** CAST is now a fully independent Telegram presence.
