import os
import requests
from telegram import Bot

# Telegram credentials (from GitHub Secrets)
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# File paths
DOMAIN_FILE = "old_domains_with_bounties.txt"
SOURCE_FILE = "old_source_code_with_bounties.txt"

# URLs
DOMAIN_URL = "https://raw.githubusercontent.com/zricethezav/h1domains/refs/heads/master/domains_with_bounties.txt"
SOURCE_URL = "https://raw.githubusercontent.com/zricethezav/h1domains/refs/heads/master/source_code_with_bounties.txt"


def fetch_file_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()


def load_or_create_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass  # Tạo tệp trống nếu chưa tồn tại
    with open(file_path, "r") as f:
        return f.read().splitlines()


def save_file_content(file_path, content):
    with open(file_path, "w") as f:
        f.write("\n".join(content))


def send_telegram_message(bot, message):
    bot.send_message(chat_id=CHAT_ID, text=message)


def check_updates():
    # Initialize Telegram Bot
    bot = Bot(token=TELEGRAM_API_TOKEN)

    # Check for domain updates
    new_domains = fetch_file_content(DOMAIN_URL)
    old_domains = load_or_create_file(DOMAIN_FILE)
    added_domains = set(new_domains) - set(old_domains)

    if added_domains:
        message = f"🆕 New domains added:\n" + "\n".join(added_domains)
        send_telegram_message(bot, message)
        save_file_content(DOMAIN_FILE, new_domains)

    # Check for source code updates
    new_sources = fetch_file_content(SOURCE_URL)
    old_sources = load_or_create_file(SOURCE_FILE)
    added_sources = set(new_sources) - set(old_sources)

    if added_sources:
        message = f"🆕 New source codes added:\n" + "\n".join(added_sources)
        send_telegram_message(bot, message)
        save_file_content(SOURCE_FILE, new_sources)


if __name__ == "__main__":
    check_updates()
