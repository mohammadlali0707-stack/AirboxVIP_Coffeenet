import sqlite3
import datetime
import os
from typing import Optional, List, Dict, Any

try:
    import telegram_bot.config as bot_config
    DEFAULT_DB_PATH = getattr(bot_config, "DB_PATH", "data/airboxvip.db")
except Exception:
    DEFAULT_DB_PATH = "data/airboxvip.db"

DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path if db_path is not None else DB_PATH
    if path != ":memory:":
        dirname = os.path.dirname(os.path.abspath(path))
        if dirname:
            os.makedirs(dirname, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('PRAGMA journal_mode=WAL;')
    except Exception:
        pass
    return conn


def init_db(db_path: Optional[str] = None):
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Table 1: published_posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            caption TEXT,
            image_url TEXT,
            message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: customer_orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            service_type TEXT,
            details TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 3: vouchers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vouchers (
            code TEXT PRIMARY KEY,
            duration_minutes INTEGER NOT NULL DEFAULT 60,
            upload_mb INTEGER NOT NULL DEFAULT 100,
            download_mb INTEGER NOT NULL DEFAULT 500,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            used_by TEXT,
            used_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comment TEXT
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_vouchers_is_active ON vouchers (is_active)
    ''')

    conn.commit()
    conn.close()


def save_post(topic, caption, image_url, message_id, db_path=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO published_posts (topic, caption, image_url, message_id)
        VALUES (?, ?, ?, ?)
    ''', (topic, caption, image_url, message_id))
    conn.commit()
    conn.close()


def is_topic_recently_published(topic, hours=24, db_path=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)
    cursor.execute('''
        SELECT COUNT(*) FROM published_posts 
        WHERE topic = ? AND created_at > ?
    ''', (topic, time_threshold.strftime('%Y-%m-%d %H:%M:%S')))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def add_order(customer_name, phone, service_type, details="", db_path=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customer_orders (customer_name, phone, service_type, details)
        VALUES (?, ?, ?, ?)
    ''', (customer_name, phone, service_type, details))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id


# Voucher operations for admin commands (/vouchers, /revoke, /stats)

def add_voucher(
    code: str,
    duration_minutes: int = 60,
    upload_mb: int = 100,
    download_mb: int = 500,
    is_active: bool = True,
    used_by: Optional[str] = None,
    used_at: Optional[str] = None,
    created_at: Optional[str] = None,
    comment: Optional[str] = None,
    db_path: Optional[str] = None,
) -> str:
    clean_code = code.upper().strip()
    created = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT OR REPLACE INTO vouchers (
            code, duration_minutes, upload_mb, download_mb,
            is_active, used_by, used_at, created_at, comment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            clean_code,
            duration_minutes,
            upload_mb,
            download_mb,
            1 if is_active else 0,
            used_by,
            used_at,
            created,
            comment,
        ),
    )
    conn.commit()
    conn.close()
    return clean_code


def get_voucher(code: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not code:
        return None
    clean_code = code.upper().strip()
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM vouchers WHERE UPPER(TRIM(code)) = ?",
        (clean_code,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_vouchers(
    active_only: bool = False,
    limit: Optional[int] = None,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM vouchers"
    params = []
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY created_at DESC"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


get_all_vouchers = list_vouchers


def revoke_voucher(code: str, db_path: Optional[str] = None) -> bool:
    if not code:
        return False
    clean_code = code.upper().strip()
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE vouchers SET is_active = 0 WHERE UPPER(TRIM(code)) = ?",
        (clean_code,),
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def count_vouchers(active_only: bool = False, db_path: Optional[str] = None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if active_only:
        cursor.execute("SELECT COUNT(*) FROM vouchers WHERE is_active = 1")
    else:
        cursor.execute("SELECT COUNT(*) FROM vouchers")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def count_vouchers_today(db_path: Optional[str] = None) -> int:
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vouchers WHERE created_at LIKE ?", (f"{today}%",))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_voucher_stats(db_path: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vouchers")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM vouchers WHERE is_active = 1")
    active = cursor.fetchone()[0]
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM vouchers WHERE created_at LIKE ?", (f"{today}%",))
    today_count = cursor.fetchone()[0]
    conn.close()
    return {
        "total_vouchers": total,
        "active_vouchers": active,
        "today_vouchers": today_count,
    }


def delete_voucher(code: str, db_path: Optional[str] = None) -> bool:
    if not code:
        return False
    clean_code = code.upper().strip()
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vouchers WHERE UPPER(TRIM(code)) = ?", (clean_code,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def clear_vouchers(db_path: Optional[str] = None) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vouchers")
    conn.commit()
    conn.close()
