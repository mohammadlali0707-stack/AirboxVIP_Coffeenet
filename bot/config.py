import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    bot_token: str = os.getenv("BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
    admin_user_ids: list = [
        int(x)
        for x in (os.getenv("ADMIN_USER_IDS") or os.getenv("ADMIN_CHAT_IDS", "")).split(",")
        if x.strip() and x.strip().isdigit()
    ]
    db_path: str = os.getenv("DB_PATH", "data/airboxvip.db")
    default_duration_minutes: int = int(os.getenv("DEFAULT_DURATION_MINUTES", "60"))
    default_download_mb: int = int(os.getenv("DEFAULT_DOWNLOAD_MB", "500"))
    default_upload_mb: int = int(os.getenv("DEFAULT_UPLOAD_MB", "100"))

    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
        self.admin_user_ids = [
            int(x)
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

    def is_admin(self, user_id) -> bool:
        if user_id is None:
            return False
        try:
            return int(user_id) in self.admin_user_ids
        except (ValueError, TypeError):
            return False


config = Config()
AppConfig = Config


