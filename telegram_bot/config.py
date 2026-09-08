import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@airboxvipcoffeenet")

# Admin Users (Comma-separated Telegram User IDs)
ADMIN_USER_IDS = [
    int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()
]

# Default Branding & Links
CHANNEL_BRANDING = "@airboxvipcoffeenet"
SUPPORT_LINK = "https://t.me/airboxvip_admin"
WEBSITE_LINK = "https://airboxvip.com"
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
