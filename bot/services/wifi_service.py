from typing import Dict, List, Optional
from datetime import datetime, timezone
from bot.models.voucher import Voucher
from bot.services.router_client import RouterClientInterface, MockRouterClient
from bot.database import Database
from bot.config import config


class WiFiService:
    def __init__(
        self,
        router_client: Optional[RouterClientInterface] = None,
        db: Optional[Database] = None,
        db_path: Optional[str] = None,
    ):
        self.router = router_client or MockRouterClient()
        if db is not None:
            self.db = db
        elif db_path is not None:
            self.db = Database(db_path=db_path)
        else:
            self.db = Database()
        self._cache: Dict[str, Voucher] = {}

    @property
    def _vouchers(self) -> Dict[str, Voucher]:
        """Backward-compatible access to vouchers dictionary."""
        return {v.code: v for v in self.list_vouchers()}

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

        self.db.add_voucher(voucher)
        self._cache[voucher.code] = voucher
        return voucher

    def get_voucher(self, code: str) -> Optional[Voucher]:
        norm_code = code.upper().strip()
        voucher = self.db.get_voucher(norm_code)
        if voucher is None:
            return None
        if norm_code in self._cache:
            cached = self._cache[norm_code]
            cached.duration_minutes = voucher.duration_minutes
            cached.upload_limit_mb = voucher.upload_limit_mb
            cached.download_limit_mb = voucher.download_limit_mb
            cached.is_active = voucher.is_active
            cached.used_by = voucher.used_by
            cached.used_at = voucher.used_at
            cached.created_at = voucher.created_at
            cached.comment = voucher.comment
            return cached
        self._cache[norm_code] = voucher
        return voucher

    def redeem_voucher(self, code: str, user_id: str) -> bool:
        voucher = self.get_voucher(code)
        if not voucher or not voucher.is_active or voucher.used_by is not None:
            return False
        voucher.used_by = str(user_id)
        voucher.used_at = datetime.now(timezone.utc).isoformat()
        self.db.update_voucher(voucher)
        return True

    def revoke_voucher(self, code: str) -> bool:
        voucher = self.get_voucher(code)
        if not voucher:
            return False
        voucher.is_active = False
        self.db.update_voucher(voucher)
        self.router.remove_hotspot_user(voucher.code)
        return True

    def list_vouchers(self, active_only: bool = False, limit: Optional[int] = None) -> List[Voucher]:
        vouchers = self.db.list_vouchers(active_only=active_only, limit=limit)
        result = []
        for v in vouchers:
            if v.code in self._cache:
                cached = self._cache[v.code]
                cached.duration_minutes = v.duration_minutes
                cached.upload_limit_mb = v.upload_limit_mb
                cached.download_limit_mb = v.download_limit_mb
                cached.is_active = v.is_active
                cached.used_by = v.used_by
                cached.used_at = v.used_at
                cached.created_at = v.created_at
                cached.comment = v.comment
                result.append(cached)
            else:
                self._cache[v.code] = v
                result.append(v)
        return result

    def get_system_status(self) -> dict:
        router_status = "Online" if self.router.ping_router() else "Offline"
        total_vouchers = self.db.count_vouchers()
        active_vouchers = self.db.count_vouchers(active_only=True)
        return {
            "router_status": router_status,
            "total_vouchers": total_vouchers,
            "active_vouchers": active_vouchers,
            "active_sessions": len(self.router.list_active_sessions()),
        }

