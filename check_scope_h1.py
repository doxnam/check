import os
import asyncio
import requests
from telegram import Bot

# Telegram Bot token và Chat ID từ môi trường
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TELEGRAM_API_TOKEN)

# URLs cần kiểm tra
DOMAIN_URL = "https://raw.githubusercontent.com/zricethezav/h1domains/refs/heads/master/domains_with_bounties.txt"
SOURCE_CODE_URL = "https://raw.githubusercontent.com/zricethezav/h1domains/refs/heads/master/source_code_with_bounties.txt"

# Hàm lấy nội dung từ URL
def fetch_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return set(response.text.splitlines())

# Hàm kiểm tra sự khác biệt và gửi tin nhắn
async def check_and_notify():
    updates = []

    # Kiểm tra domains_with_bounties.txt
    domain_file = "old_domains_with_bounties.txt"
    new_domains = fetch_content(DOMAIN_URL)
    old_domains = set()

    if os.path.exists(domain_file):
        with open(domain_file, "r") as f:
            old_domains = set(f.read().splitlines())
    added_domains = new_domains - old_domains

    if added_domains:
        updates.append(f"🆕 **New Domains Added:**\n" + "\n".join(added_domains))
        with open(domain_file, "w") as f:
            f.write("\n".join(new_domains))

    # Kiểm tra source_code_with_bounties.txt
    source_file = "old_source_code_with_bounties.txt"
    new_sources = fetch_content(SOURCE_CODE_URL)
    old_sources = set()

    if os.path.exists(source_file):
        with open(source_file, "r") as f:
            old_sources = set(f.read().splitlines())
    added_sources = new_sources - old_sources

    if added_sources:
        updates.append(f"🆕 **New Source Codes Added:**\n" + "\n".join(added_sources))
        with open(source_file, "w") as f:
            f.write("\n".join(new_sources))

    # Gửi thông báo nếu có cập nhật
    if updates:
        message = "\n\n".join(updates)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# Hàm chính để chạy
if __name__ == "__main__":
    asyncio.run(check_and_notify())
