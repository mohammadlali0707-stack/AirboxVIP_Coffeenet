from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional
import secrets
import string


@dataclass
class Voucher:
    code: str
    duration_minutes: int
    upload_limit_mb: int
    download_limit_mb: int
    created_at: str
    is_active: bool = True
    used_by: Optional[str] = None
    used_at: Optional[str] = None
    comment: Optional[str] = None

    @classmethod
    def generate(
        cls,
        duration_minutes: int = 60,
        upload_limit_mb: int = 500,
        download_limit_mb: int = 1024,
        code_length: int = 6,
        comment: Optional[str] = None,
    ) -> "Voucher":
        chars = string.ascii_uppercase + string.digits
        # exclude ambiguous characters like 0, O, 1, I
        unambiguous = "".join(c for c in chars if c not in "0O1I")
        code = "".join(secrets.choice(unambiguous) for _ in range(code_length))
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            code=code,
            duration_minutes=duration_minutes,
            upload_limit_mb=upload_limit_mb,
            download_limit_mb=download_limit_mb,
            created_at=now,
            is_active=True,
            comment=comment,
        )

    @property
    def upload_mb(self) -> int:
        return self.upload_limit_mb

    @property
    def download_mb(self) -> int:
        return self.download_limit_mb

    def to_dict(self) -> dict:
        d = asdict(self)
        d["upload_mb"] = self.upload_limit_mb
        d["download_mb"] = self.download_limit_mb
        return d

