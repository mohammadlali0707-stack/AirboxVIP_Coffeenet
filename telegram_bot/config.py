import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Credentials
TELEGRAM_TOKEN = (
    os.getenv("TELEGRAM_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("BOT_TOKEN")
    or ""
)
TELEGRAM_BOT_TOKEN = TELEGRAM_TOKEN
BOT_TOKEN = TELEGRAM_TOKEN
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@airboxvipcoffeenet")

# Admin Users (Comma-separated Telegram User IDs)
ADMIN_USER_IDS = [
    int(x.strip())
    for x in (os.getenv("ADMIN_USER_IDS") or os.getenv("ADMIN_CHAT_IDS", "")).split(",")
    if x.strip() and x.strip().isdigit()
]
ADMIN_CHAT_IDS = ADMIN_USER_IDS


def is_admin(user_id) -> bool:
    if user_id is None:
        return False
    try:
        uid = int(user_id)
        return uid in ADMIN_CHAT_IDS or uid in ADMIN_USER_IDS or (config and config.is_admin(uid))
    except (ValueError, TypeError):
        return False

# Default Branding & Links
CHANNEL_BRANDING = "@airboxvipcoffeenet"
SUPPORT_LINK = "https://t.me/airboxvip_admin"
WEBSITE_LINK = "https://airboxvip.com"
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# WiFi & Database Configuration
DB_PATH = os.getenv("DB_PATH", "data/airboxvip.db")
DEFAULT_DURATION_MINUTES = int(os.getenv("DEFAULT_DURATION_MINUTES", "60"))
DEFAULT_DOWNLOAD_MB = int(os.getenv("DEFAULT_DOWNLOAD_MB", "500"))
DEFAULT_UPLOAD_MB = int(os.getenv("DEFAULT_UPLOAD_MB", "100"))


class Config:
    def __init__(self):
        self.bot_token = (
            os.getenv("TELEGRAM_TOKEN")
            or os.getenv("TELEGRAM_BOT_TOKEN")
            or os.getenv("BOT_TOKEN")
            or ""
        )
        self.telegram_token = self.bot_token
        self.admin_user_ids = [
            int(x.strip())
            for x in (os.getenv("ADMIN_USER_IDS") or os.getenv("ADMIN_CHAT_IDS", "")).split(",")
            if x.strip() and x.strip().isdigit()
        ]
        self.db_path = os.getenv("DB_PATH", "data/airboxvip.db")
        self.default_duration_minutes = int(os.getenv("DEFAULT_DURATION_MINUTES", "60"))
        self.default_download_mb = int(os.getenv("DEFAULT_DOWNLOAD_MB", "500"))
        self.default_upload_mb = int(os.getenv("DEFAULT_UPLOAD_MB", "100"))

    @property
    def admin_chat_ids(self) -> list:
        return self.admin_user_ids

    @admin_chat_ids.setter
    def admin_chat_ids(self, val: list):
        self.admin_user_ids = val

    @property
    def ADMIN_CHAT_IDS(self) -> list:
        return self.admin_user_ids

    @ADMIN_CHAT_IDS.setter
    def ADMIN_CHAT_IDS(self, val: list):
        self.admin_user_ids = val

    def is_admin(self, user_id) -> bool:
        if user_id is None:
            return False
        try:
            return int(user_id) in self.admin_user_ids
        except (ValueError, TypeError):
            return False


config = Config()
AppConfig = Config
