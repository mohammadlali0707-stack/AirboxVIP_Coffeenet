import os
from dataclasses import dataclass, field
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v


@dataclass
class AppConfig:
    bot_token: str = field(
        default_factory=lambda: os.getenv("BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
    )
    admin_user_ids: List[int] = field(default_factory=lambda: [
        int(x.strip())
        for x in (os.getenv("ADMIN_USER_IDS") or os.getenv("ADMIN_CHAT_IDS", "")).split(",")
        if x.strip().isdigit()
    ])
    db_path: str = field(
        default_factory=lambda: os.getenv("DB_PATH", "data/airboxvip.db")
    )
    router_host: str = field(
        default_factory=lambda: os.getenv("ROUTER_HOST", "127.0.0.1")
    )
    router_port: int = field(
        default_factory=lambda: int(os.getenv("ROUTER_PORT", "8728"))
    )
    router_user: str = field(
        default_factory=lambda: os.getenv("ROUTER_USER", "admin")
    )
    router_password: str = field(
        default_factory=lambda: os.getenv("ROUTER_PASSWORD", "")
    )
    default_duration_minutes: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_DURATION_MINUTES", os.getenv("DEFAULT_VOUCHER_DURATION_MINUTES", "60")))
    )
    default_upload_mb: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_UPLOAD_MB", os.getenv("DEFAULT_UPLOAD_LIMIT_MB", "100")))
    )
    default_download_mb: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_DOWNLOAD_MB", os.getenv("DEFAULT_DOWNLOAD_LIMIT_MB", "500")))
    )
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/airboxvip.db")
    )

    @property
    def admin_chat_ids(self) -> List[int]:
        return self.admin_user_ids

    @admin_chat_ids.setter
    def admin_chat_ids(self, val: List[int]):
        self.admin_user_ids = val

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_user_ids


config = AppConfig()

