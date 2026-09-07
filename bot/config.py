import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class AppConfig:
    bot_token: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "")
    )
    admin_chat_ids: List[int] = field(default_factory=lambda: [
        int(x.strip())
        for x in os.getenv("ADMIN_CHAT_IDS", "").split(",")
        if x.strip().isdigit()
    ])
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
        default_factory=lambda: int(os.getenv("DEFAULT_VOUCHER_DURATION_MINUTES", "60"))
    )
    default_upload_mb: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_UPLOAD_LIMIT_MB", "500"))
    )
    default_download_mb: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_DOWNLOAD_LIMIT_MB", "1024"))
    )
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///coffeenet.db")
    )

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_chat_ids


config = AppConfig()
