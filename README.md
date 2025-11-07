# Shopee Voucher Bot

This is a Telegram bot that automatically fetches Shopee vouchers from different APIs (Accesstrade, Piggi) and sends them to a specific Telegram group topic just before they become active.

## Features

*   Fetches vouchers from multiple APIs (Accesstrade, Piggi).
*   Schedules sending vouchers to a Telegram group topic 15 seconds before they become active.
*   Avoids sending duplicate vouchers by storing sent voucher codes in a SQLite database.
*   Provides a command-line interface (CLI) to monitor the bot's status, upcoming vouchers, and logs.
*   Sends vouchers with an image, name, code, value, start time, end time, and a "Use Now" button.

## Technologies Used

*   Python
*   `requests` for making API calls.
*   `apscheduler` for scheduling tasks.
*   `python-telegram-bot` for interacting with the Telegram Bot API.
*   `sqlite3` for the database.
*   `pydantic` for data validation.
*   `pystyle` for styling the CLI.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/trongthaohub/Bot_Voucher.git
    cd Bot_Voucher
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the bot:**

    *   Open the `config.py` file and fill in your details:
        *   `TELEGRAM_TOKEN`: Your Telegram bot token.
        *   `GROUP_ID`: The ID of the Telegram group where you want to send the vouchers.
        *   `TOPIC_ID`: The ID of the topic within the group.
        *   `ACCESSTRADE_TOKEN`: Your Accesstrade API token.

## Usage

Run the bot with the following command:

```bash
python main.py
```

The bot will start fetching vouchers and sending them to the specified Telegram group topic. You can monitor the bot's activity in the CLI.

## Project Structure

```
├───apis
│   ├───__init__.py
│   ├───accesstrade_api.py
│   └───piggi_api.py
├───models
│   └───voucher.py
├───config.py
├───database.py
├───main.py
├───README.md
├───scheduler.py
├───telegram_bot.py
└───vouchers.db
```
