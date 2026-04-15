# PSOAS Flat Exchange Monitor

Monitors the [PSOAS Flat Exchange](https://www.psoas.fi/en/flat-exchange/) page for new apartment listings and sends Telegram notifications for relevant ones.

## What it does

- Fetches the PSOAS Flat Exchange listings page
- Parses all "Available For Rent" listing cards
- Filters for Studio or Family apartments at ≤ 500 €/month
- Stores seen listings in SQLite so you never get duplicate notifications
- Sends a Telegram message for each new matching listing
- Displays a formatted table in the terminal

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 3. Get your Telegram chat ID

1. Start a chat with your new bot (send it `/start`)
2. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
3. Find `"chat":{"id":123456789}` — that number is your chat ID

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

## Usage

### Test Telegram connection

```bash
python main.py --test-telegram
```

### Run once (show listings + notify new ones)

```bash
python main.py --once
```

### Run once without sending messages

```bash
python main.py --once --dry-run
```

### Watch mode (check every 15 minutes)

```bash
python main.py --watch
```

### Watch with custom interval (in seconds)

```bash
python main.py --watch --interval 600
```

### Export stored listings to CSV

```bash
python main.py --export-csv listings.csv
```

### Verbose logging

Add `-v` to any command:

```bash
python main.py --once -v
```

## Running as a cron job (Linux/macOS)

```bash
crontab -e
```

Add (runs every 15 minutes):

```
*/15 * * * * cd /path/to/ouluflatsearcher && /path/to/python main.py --once >> cron.log 2>&1
```

## Running as a systemd service (Linux)

Create `/etc/systemd/system/psoas-monitor.service`:

```ini
[Unit]
Description=PSOAS Flat Exchange Monitor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/ouluflatsearcher
ExecStart=/path/to/python main.py --watch
Restart=on-failure
RestartSec=60
EnvironmentFile=/path/to/ouluflatsearcher/.env

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now psoas-monitor
sudo systemctl status psoas-monitor
```

## Running tests

```bash
pytest tests/ -v
```

## Filtering criteria

Current defaults (edit `config.py` to change):

| Setting | Value |
|---------|-------|
| Allowed types | Studio, Family |
| Max rent | 500 € |

## If parsing breaks

PSOAS may change their HTML. Here's what to check:

1. Run with `-v` to see debug logs
2. Check `snapshots/` folder for saved HTML when parsing returns 0 results
3. The most likely things to change are CSS class names in `parser.py`:
   - `LISTING_CARD_CLASS` — currently `card-ap-ilmoitus`
   - `TITLE_CLASS` — currently `card-ap-ilmoitus__title`
   - `LEASING_CLASS` — currently `card-ap-ilmoitus__ajankohta`
   - `CONTACT_CLASS` — currently `card-ap-ilmoitus__contact`
   - `DIRECT_LINK_CLASS` — currently `card-ap-ilmoitus__directlink`
   - `RENT_SECTION_HEADER_ID` — currently `postings`
4. Open the saved snapshot, search for listing content, and update the class names in `parser.py`

## Project structure

```
main.py          CLI entry point
scraper.py       HTTP fetching with retries
parser.py        HTML parsing (BeautifulSoup)
models.py        Pydantic data models
filters.py       Listing filter logic
storage.py       SQLite persistence
notifier.py      Telegram Bot API integration
config.py        Settings and environment
utils.py         Logging and terminal output
tests/           Unit tests
```
