# Overnight Edge

AI-generated market intelligence. Zero humans. Delivered before the market opens.

## Structure

| Path | Purpose |
|------|---------|
| `src/app/page.tsx` | Landing page (Next.js + Tailwind) |
| `subscribers.csv` | Email, tier, status, start date, Telegram ID |
| `delivery_log.csv` | Date, tier, type, subscriber count, status |
| `signal_accuracy.csv` | Date, ticker, type, confluence score, sources, outcome |
| `services/overnight_edge.py` | Daily brief generator (7:30 AM EST) |
| `services/signal_synthesizer.py` | Real-time signal detection (market hours, every 30 min) |
| `services/weekly_audit.py` | Weekly summary report (Sundays 12 PM EST) |
| `services/subscribers.py` | CLI for adding/cancelling/listing subscribers |
| `services/setup_cron.sh` | Installs all cron jobs |

## Commands

```bash
# Add subscriber
python3 services/subscribers.py add user@email.com edge     # or signal

# Cancel subscriber
python3 services/subscribers.py cancel user@email.com

# List all subscribers
python3 services/subscribers.py list

# Manual run (for testing)
python3 services/overnight_edge.py
python3 services/signal_synthesizer.py
python3 services/weekly_audit.py

# Reinstall cron jobs
bash services/setup_cron.sh
```

## Deploy to Vercel

```bash
cd /mnt/user/overnight-edge
npx vercel login                    # one-time auth
npx vercel deploy --prod            # deploy
```

## Cron Schedule

| Service | Schedule | UTC | EST |
|---------|----------|-----|-----|
| Overnight Edge | `30 12 * * 1-5` | 12:30 | 7:30 AM |
| SignalSynthesizer | `*/30 14-20 * * 1-5` + `0 21 * * 1-5` | 14:30-21:00 | 9:30 AM - 4:00 PM |
| Weekly Audit | `0 17 * * 0` | 17:00 | 12:00 PM |

## Telegram

- Bot: @OvernightEdgeBot
- Token: `8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk`
- Chat ID: `5975342168`

## Stripe Links

- Daily Brief ($49/mo): `prod_UTd168i0Iw8b3M`
- SignalSynthesizer ($149/mo): `prod_UTd2L2yQEam5Cl`
