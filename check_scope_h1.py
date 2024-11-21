import os
import asyncio
import requests
from telegram import Bot
from telegram.helpers import escape_markdown

# Telegram Bot token và Chat ID từ môi trường
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TELEGRAM_API_TOKEN)

# URLs cần kiểm tra
DOMAIN_URL = "https://raw.githubusercontent.com/zricethezav/h1domains/refs/heads/master/domains_with_bounties.txt"
SOURCE_CODE_URL = "https://raw.githubusercontent.com/zricethezav/h1domains/refs/heads/master/source_code_with_bounties.txt"
MAX_LINES = 80  # Số dòng tối đa cho mỗi tin nhắn

def fetch_content(url):
    """Lấy nội dung từ URL."""
    response = requests.get(url)
    response.raise_for_status()
    return set(response.text.splitlines())

def load_old_content(file_path):
    """Tải nội dung từ tệp cũ."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_content(file_path, content):
    """Lưu nội dung mới vào tệp."""
    with open(file_path, "w") as f:
        f.write("\n".join(content))

def split_message_by_lines(message, max_lines):
    """Chia nội dung tin nhắn thành từng phần theo số dòng."""
    lines = message.split("\n")
    return ["\n".join(lines[i:i + max_lines]) for i in range(0, len(lines), max_lines)]

async def send_updates(bot, chat_id, header, updates):
    """Gửi các bản cập nhật, xử lý ký tự đặc biệt và chia nhỏ theo dòng."""
    if updates:
        # Ghép header và nội dung cập nhật
        message = f"{header}\n" + "\n".join(updates)
        # Chia tin nhắn theo số dòng
        parts = split_message_by_lines(message, MAX_LINES)
        for part in parts:
            # Xử lý ký tự đặc biệt trong Markdown trước khi gửi
            escaped_part = escape_markdown(part, version=2)
            await bot.send_message(chat_id=chat_id, text=escaped_part, parse_mode="MarkdownV2")

async def check_and_notify():
    # Kiểm tra domains_with_bounties.txt
    domain_file = "old_domains_with_bounties.txt"
    new_domains = fetch_content(DOMAIN_URL)
    old_domains = load_old_content(domain_file)
    added_domains = new_domains - old_domains

    # Cập nhật tệp cũ chỉ sau khi đã xử lý nội dung mới
    save_content(domain_file, new_domains)

    # Gửi cập nhật cho Domains
    if added_domains:
        await send_updates(
            bot=bot,
            chat_id=CHAT_ID,
            header="🆕 **New Domains Added:**",
            updates=sorted(added_domains)
        )
    else:
        print("No new domains added.")

    # Kiểm tra source_code_with_bounties.txt
    source_file = "old_source_code_with_bounties.txt"
    new_sources = fetch_content(SOURCE_CODE_URL)
    old_sources = load_old_content(source_file)
    added_sources = new_sources - old_sources

    # Cập nhật tệp cũ chỉ sau khi đã xử lý nội dung mới
    save_content(source_file, new_sources)

    # Gửi cập nhật cho Source Codes
    if added_sources:
        await send_updates(
            bot=bot,
            chat_id=CHAT_ID,
            header="🆕 **New Source Codes Added:**",
            updates=sorted(added_sources)
        )
    else:
        print("No new source codes added.")

# Hàm chính để chạy
if __name__ == "__main__":
    asyncio.run(check_and_notify())
