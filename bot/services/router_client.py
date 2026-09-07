from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RouterClientInterface(ABC):
    @abstractmethod
    def add_hotspot_user(
        self,
        username: str,
        password: str,
        limit_uptime: Optional[int] = None,
        limit_bytes_total: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> bool:
        """Add a hotspot user/voucher to the router."""
        pass

    @abstractmethod
    def remove_hotspot_user(self, username: str) -> bool:
        """Remove a hotspot user from the router."""
        pass

    @abstractmethod
    def list_active_sessions(self) -> List[Dict]:
        """List currently active hotspot sessions."""
        pass

    @abstractmethod
    def ping_router(self) -> bool:
        """Check router connectivity."""
        pass


class MockRouterClient(RouterClientInterface):
    """In-memory mock router client for local development and testing."""

    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.active_sessions: List[Dict] = []
        self._is_online = True

    def set_online(self, online: bool):
        self._is_online = online

    def ping_router(self) -> bool:
        return self._is_online

    def add_hotspot_user(
        self,
        username: str,
        password: str,
        limit_uptime: Optional[int] = None,
        limit_bytes_total: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> bool:
        if not self._is_online:
            return False
        self.users[username] = {
            "name": username,
            "password": password,
            "limit-uptime": limit_uptime,
            "limit-bytes-total": limit_bytes_total,
            "comment": comment,
        }
        return True

    def remove_hotspot_user(self, username: str) -> bool:
        if not self._is_online:
            return False
        if username in self.users:
            del self.users[username]
            return True
        return False

    def list_active_sessions(self) -> List[Dict]:
        if not self._is_online:
            return []
        return self.active_sessions
