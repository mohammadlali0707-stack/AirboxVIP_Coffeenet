from typing import Dict, List, Optional
from datetime import datetime, timezone
from bot.models.voucher import Voucher
from bot.services.router_client import RouterClientInterface, MockRouterClient
from bot.config import config


class WiFiService:
    def __init__(self, router_client: Optional[RouterClientInterface] = None):
        self.router = router_client or MockRouterClient()
        self._vouchers: Dict[str, Voucher] = {}

    def issue_voucher(
        self,
        duration_minutes: Optional[int] = None,
        upload_mb: Optional[int] = None,
        download_mb: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> Voucher:
        dur = duration_minutes or config.default_duration_minutes
        up = upload_mb or config.default_upload_mb
        down = download_mb or config.default_download_mb

        voucher = Voucher.generate(
            duration_minutes=dur,
            upload_limit_mb=up,
            download_limit_mb=down,
            comment=comment,
        )

        # Sync with router
        uptime_seconds = dur * 60
        bytes_total = (up + down) * 1024 * 1024
        self.router.add_hotspot_user(
            username=voucher.code,
            password=voucher.code,
            limit_uptime=uptime_seconds,
            limit_bytes_total=bytes_total,
            comment=f"AirboxVIP:{comment or 'Auto'}",
        )

        self._vouchers[voucher.code] = voucher
        return voucher

    def get_voucher(self, code: str) -> Optional[Voucher]:
        return self._vouchers.get(code.upper().strip())

    def redeem_voucher(self, code: str, user_id: str) -> bool:
        voucher = self.get_voucher(code)
        if not voucher or not voucher.is_active or voucher.used_by is not None:
            return False
        voucher.used_by = str(user_id)
        voucher.used_at = datetime.now(timezone.utc).isoformat()
        return True

    def revoke_voucher(self, code: str) -> bool:
        voucher = self.get_voucher(code)
        if not voucher:
            return False
        voucher.is_active = False
        self.router.remove_hotspot_user(voucher.code)
        return True

    def list_vouchers(self, active_only: bool = False) -> List[Voucher]:
        if active_only:
            return [v for v in self._vouchers.values() if v.is_active]
        return list(self._vouchers.values())

    def get_system_status(self) -> dict:
        router_status = "Online" if self.router.ping_router() else "Offline"
        total_vouchers = len(self._vouchers)
        active_vouchers = sum(1 for v in self._vouchers.values() if v.is_active)
        return {
            "router_status": router_status,
            "total_vouchers": total_vouchers,
            "active_vouchers": active_vouchers,
            "active_sessions": len(self.router.list_active_sessions()),
        }
