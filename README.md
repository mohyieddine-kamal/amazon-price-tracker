# Amazon Price Tracker

A Python bot that monitors a product's price on Amazon.fr, keeps a historical record, and sends a Telegram alert whenever the price drops.

## Features

- **Automated scraping** of product title and price from Amazon.fr using Playwright
- **Resilient price extraction**: handles Amazon's inconsistent price markup (multiple price blocks, empty elements, comma/period formatting) by scanning all candidate elements instead of relying on a single brittle selector
- **Price history** stored in a local SQLite database
- **Price drop detection**: compares each new scrape to the last recorded price
- **Telegram notifications** on price drops, and on scraper failures (so silent breakage never goes unnoticed)
- **Error handling**: scraping failures, Telegram failures, and unexpected errors are caught and logged without crashing the process
- **Two scheduling options**: a `cron`-based setup for production, and a pure-Python `schedule`-based alternative for simpler environments

## Tech stack

- Python 3.12
- [Playwright](https://playwright.dev/python/) (browser automation)
- SQLite (price history storage)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (secrets management)
- Telegram Bot API (notifications)

## Project structure

```
price-tracker-bot/
├── scraper.py            # Scraping logic, price comparison, orchestration
├── db.py                 # SQLite setup and queries
├── alert.py               # Telegram notification helper
├── run_with_schedule.py  # Alternative scheduler using the `schedule` library
├── requirements.txt       # Python dependencies
├── .env.example            # Template for required environment variables
└── .gitignore
```

## How it works

1. `scraper.py` launches a headless Chromium browser via Playwright and navigates to the target Amazon.fr product page.
2. It extracts the product title and price. Amazon serves the price in several places on the page (main price, strike-through price, bundled offers), some of which are empty placeholders, so the scraper collects every candidate and picks the first non-empty one.
3. The price is normalized (removing the currency symbol, handling both `,` and `.` as decimal separators) and converted to a float.
4. The last known price for this product is fetched from the SQLite database.
5. If the new price is lower, a Telegram alert is sent with the old price, the new price, and a direct link to the product.
6. The new price is recorded in the database regardless, building a historical record over time.
7. Any failure (page structure change, network issue, missing element) is caught, logged, and reported via Telegram as a scraper failure, rather than crashing silently.

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/mohyieddine-kamal/amazon-price-tracker.git
cd amazon-price-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Create a Telegram bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to get a bot token
3. Start a conversation with your new bot and send it any message
4. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser to find your `chat_id` in the response

### 3. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

```
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 4. Set the target product

Edit the `url` variable at the top of `scraper.py` to point to the Amazon.fr product page you want to track.

## Usage

### Run once manually

```bash
python3 scraper.py
```

### Run continuously with the `schedule` library

```bash
python3 run_with_schedule.py
```

Runs an infinite loop in the foreground, checking the price every hour. Useful for quick testing or environments without cron.

### Run automatically with cron (recommended for production)

Open your crontab:

```bash
crontab -e
```

Add a line to run the scraper every hour:

```
0 * * * * cd /path/to/price-tracker-bot && /path/to/price-tracker-bot/venv/bin/python3 scraper.py >> /path/to/price-tracker-bot/cron.log 2>&1
```

## Example output

```
Dernier prix connu: 19.49
Baisse de prix !
Uineer Wireless Mouse Tri-Mode for 3 Devices - BT5.0/4.0 and 2.4GHz
19.49e -> 18.52e
https://www.amazon.fr/dp/B0DCVMN51Z
{'title': 'Uineer Wireless Mouse Tri-Mode for 3 Devices - BT5.0/4.0 and 2.4GHz', 'price': 18.52}
```

## Known limitations

- Tracks a single hardcoded product URL; not yet configurable for a list of products
- Amazon's page structure can change at any time, which may require updating the CSS selectors in `get_product_info`
- No retry logic for transient network failures (a single failed run is logged and reported, but not automatically retried)

## Possible improvements

- Support tracking multiple products from a config file (e.g. `products.json`)
- Replace `print` statements with proper logging (e.g. Python's `logging` module)
- Add automatic retries with backoff for transient scraping failures
- Add a small CLI to add/remove tracked products without editing code

## License

MIT
