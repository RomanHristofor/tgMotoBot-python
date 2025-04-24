# Telegram tgMotoBot (Python)

tgMotoBot is a Python-based Telegram bot designed to scrape motorcycle listings from [moto.av.by](https://moto.av.by) and deliver filtered results directly to your Telegram account. The bot allows users to specify search criteria (brand, year, price range) and fetches relevant listings.

## Features

- **Interactive Motorcycle Search**: Users can select a motorcycle brand, model, year, and maximum price using Telegram keyboards and inline buttons.
- **Web Scraping**: Scrapes motorcycle listings from [moto.av.by](https://moto.av.by) using `requests` and `BeautifulSoup`.
- **Telegram Automation**: Built using `python-telegram-bot` for seamless interaction with Telegram API, including custom keyboards and error handling.
- **Logging and Error Handling**: Implements logging for debugging and robust error handling for network issues.
- **Anti-Ban Considerations**: Includes `User-Agent` headers to avoid scraping bans and timeout handling for reliable operation.
- **Scalability Potential**: Designed with modularity, ready for optimization (e.g., async requests, multithreading) and integration with databases (e.g., Pandas).

## Prerequisites

Before running tgMotoBot, ensure you have the following:

- Python 3.7+ (tested with Python 3.12)
- A Telegram API token (obtained via @BotFather)
- Optional: Proxy server (if Telegram is blocked in your region)

## Installation

1. Clone the repository:
   ```bash
   git clone [your-repo-link]
   cd tgMotoBot-python
   ```
