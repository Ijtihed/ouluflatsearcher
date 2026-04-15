# PSOAS Flat Exchange Monitor

Scrapes the [PSOAS Flat Exchange](https://www.psoas.fi/en/flat-exchange/) page every hour and sends me a Telegram message when a new affordable listing appears.

## Why scrape this random website

I needed cheap short-term housing in Oulu for an internship. PSOAS tenants post summer sublets on their flat exchange page, but listings disappear super quickly. This bot watches the page so I don't have to.

## How it works

1. Fetches the PSOAS Flat Exchange page
2. Parses all "Available For Rent" listing cards
3. Filters for **Studio** or **Family** apartments at **≤ 550 €/month**
4. Stores seen listings in SQLite so nothing gets sent twice
5. Sends a Telegram message for each new match

Runs hourly via GitHub Actions. Can also run locally with `python main.py --once` or `python main.py --watch`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

```
TELEGRAM_BOT_TOKEN=your-token-from-botfather
TELEGRAM_CHAT_ID=your-chat-id
```

To get these: message [@BotFather](https://t.me/BotFather) on Telegram to create a bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` after sending your bot a message to find your chat ID.

## Usage

```bash
python main.py --once           # check once and notify
python main.py --once --dry-run # check once, no messages
python main.py --watch          # loop every 15 min
python main.py --test-telegram  # verify bot works
```

## If parsing breaks

PSOAS may change their HTML. Update the CSS selectors at the top of `parser.py`. Run with `-v` for debug logs. Failed parses save HTML snapshots to `snapshots/`.
