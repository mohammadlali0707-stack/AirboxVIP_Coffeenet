import sqlite3
import os
from typing import Optional, List
from bot.models.voucher import Voucher
from bot.config import config


class Database:
    """SQLite database persistence for AirboxVIP Coffeenet vouchers."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path is not None else config.db_path
        if self.db_path != ":memory:":
            dirname = os.path.dirname(os.path.abspath(self.db_path))
            if dirname:
                os.makedirs(dirname, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        conn = self.get_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vouchers (
                    code TEXT PRIMARY KEY,
                    duration_minutes INTEGER NOT NULL,
                    upload_mb INTEGER NOT NULL,
                    download_mb INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    used_by TEXT,
                    used_at TEXT,
                    created_at TEXT NOT NULL,
                    comment TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_vouchers_is_active ON vouchers (is_active)
            """)

    @staticmethod
    def _row_to_voucher(row: sqlite3.Row) -> Voucher:
        return Voucher(
            code=row["code"],
            duration_minutes=row["duration_minutes"],
            upload_limit_mb=row["upload_mb"],
            download_limit_mb=row["download_mb"],
            created_at=row["created_at"],
            is_active=bool(row["is_active"]),
            used_by=row["used_by"],
            used_at=row["used_at"],
            comment=row["comment"],
        )

    def add_voucher(self, voucher: Voucher) -> None:
        conn = self.get_connection()
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO vouchers (
                    code, duration_minutes, upload_mb, download_mb,
                    is_active, used_by, used_at, created_at, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    voucher.code,
                    voucher.duration_minutes,
                    voucher.upload_limit_mb,
                    voucher.download_limit_mb,
                    1 if voucher.is_active else 0,
                    voucher.used_by,
                    voucher.used_at,
                    voucher.created_at,
                    voucher.comment,
                ),
            )

    def update_voucher(self, voucher: Voucher) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.execute(
                """
                UPDATE vouchers SET
                    duration_minutes = ?,
                    upload_mb = ?,
                    download_mb = ?,
                    is_active = ?,
                    used_by = ?,
                    used_at = ?,
                    created_at = ?,
                    comment = ?
                WHERE code = ?
                """,
                (
                    voucher.duration_minutes,
                    voucher.upload_limit_mb,
                    voucher.download_limit_mb,
                    1 if voucher.is_active else 0,
                    voucher.used_by,
                    voucher.used_at,
                    voucher.created_at,
                    voucher.comment,
                    voucher.code,
                ),
            )
            return cursor.rowcount > 0

    def get_voucher(self, code: str) -> Optional[Voucher]:
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM vouchers WHERE code = ?",
            (code.upper().strip(),),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_voucher(row)
        return None

    def list_vouchers(self, active_only: bool = False, limit: Optional[int] = None) -> List[Voucher]:
        conn = self.get_connection()
        query = "SELECT * FROM vouchers"
        params = []
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor = conn.execute(query, params)
        return [self._row_to_voucher(row) for row in cursor.fetchall()]

    def count_vouchers(self, active_only: bool = False) -> int:
        conn = self.get_connection()
        if active_only:
            cursor = conn.execute("SELECT COUNT(*) FROM vouchers WHERE is_active = 1")
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM vouchers")
        return cursor.fetchone()[0]

    def count_vouchers_today(self) -> int:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conn = self.get_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM vouchers WHERE created_at LIKE ?", (f"{today}%",))
        return cursor.fetchone()[0]

    def delete_voucher(self, code: str) -> bool:
        conn = self.get_connection()
        with conn:
            cursor = conn.execute(
                "DELETE FROM vouchers WHERE code = ?",
                (code.upper().strip(),),
            )
            return cursor.rowcount > 0

    def clear_all(self) -> None:
        """Clear all vouchers - useful for test cleanup."""
        conn = self.get_connection()
        with conn:
            conn.execute("DELETE FROM vouchers")

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
