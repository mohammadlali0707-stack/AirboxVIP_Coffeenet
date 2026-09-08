import functools
import inspect
from typing import Optional
from bot.services.wifi_service import WiFiService
from bot.config import config


def is_admin(user_id: int) -> bool:
    """Check if user_id is an authorized admin."""
    if user_id is None:
        return False
    try:
        return int(user_id) in config.admin_user_ids
    except (ValueError, TypeError):
        return False


def require_admin(func):
    """Guard decorator that restricts execution to admin users."""
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id if update and update.effective_user else None
            if not is_admin(user_id):
                if update and update.message:
                    await update.message.reply_text("⛔ دسترسی ندارید")
                return "⛔ دسترسی ندارید"
            return await func(update, context, *args, **kwargs)
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            if user_id is None and len(args) > 1 and isinstance(args[1], int):
                user_id = args[1]
            elif user_id is None and len(args) > 0 and isinstance(args[0], int):
                user_id = args[0]
            if user_id is not None and not is_admin(user_id):
                return "⛔ دسترسی ندارید"
            return func(*args, **kwargs)
        return sync_wrapper


def handle_admin(user_id: int) -> str:
    """Return admin panel menu text in Persian."""
    if not is_admin(user_id):
        return "⛔ دسترسی ندارید"
    return (
        "👑 **پنل مدیریت AirboxVIP Coffeenet**\n\n"
        "دستورات مدیریت:\n"
        "• /admin - نمایش منوی مدیریت\n"
        "• /vouchers - مشاهده ۱۰ ووچر فعال اخیر\n"
        "• /revoke <code> - غیرفعال‌سازی ووچر با کد مشخص\n"
        "• /stats - آمار و وضعیت سیستم\n"
        "• /status - وضعیت شبکه کافه"
    )


def handle_vouchers(wifi_service: WiFiService, user_id: int) -> str:
    """Return formatted table of active vouchers or empty message."""
    if not is_admin(user_id):
        return "⛔ دسترسی ندارید"

    active_vouchers = wifi_service.list_vouchers(active_only=True, limit=10)
    if not active_vouchers:
        return "هیچ کد فعالی وجود ندارد"

    header = "code | duration | used_by | created_at"
    separator = "---|---|---|---"
    rows = [header, separator]
    for v in active_vouchers:
        used = str(v.used_by) if v.used_by else "-"
        created = str(v.created_at)[:19] if v.created_at else "-"
        rows.append(f"`{v.code}` | {v.duration_minutes}m | {used} | {created}")

    return "📋 **لیست ووچرهای فعال:**\n\n" + "\n".join(rows)


def handle_revoke(
    wifi_service: WiFiService,
    user_id: int,
    code: str,
) -> str:
    """Revoke a voucher by code. Returns Persian status message."""
    if not is_admin(user_id):
        return "⛔ دسترسی ندارید"

    if not code or not code.strip():
        return "لطفاً کد ووچر را وارد کنید:\n`/revoke <code>`"

    clean_code = code.upper().strip()
    if wifi_service.revoke_voucher(clean_code):
        return f"✅ کد `{clean_code}` غیرفعال شد"
    return "❌ کد یافت نشد"


def handle_stats(wifi_service: WiFiService, user_id: int) -> str:
    """Return system statistics formatted in Persian with emoji."""
    if not is_admin(user_id):
        return "⛔ دسترسی ندارید"

    status = wifi_service.get_system_status()
    router_status = status.get("router_status", "Unknown")
    router_fa = "🟢 آنلاین" if router_status == "Online" else "🔴 آفلاین"
    today_vouchers = status.get("today_vouchers", 0)
    active_now = status.get("active_vouchers", 0)
    total_vouchers = status.get("total_vouchers", 0)
    active_sessions = status.get("active_sessions", 0)

    return (
        "📊 **آمار سامانه AirboxVIP Coffeenet:**\n\n"
        f"📅 کل ووچرهای امروز: {today_vouchers}\n"
        f"🟢 ووچرهای فعال اکنون: {active_now}\n"
        f"📡 وضعیت روتر: {router_fa} ({router_status})\n"
        f"👥 نشست‌های فعال: {active_sessions}\n"
        f"🎟️ مجموع کل ووچرها: {total_vouchers}"
    )


# Backward-compatible helper functions
def handle_issue(
    wifi_service: WiFiService,
    user_id: int,
    duration_minutes: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    if not is_admin(user_id):
        return "⛔ شما دسترسی به دستورات مدیریت را ندارید."

    voucher = wifi_service.issue_voucher(
        duration_minutes=duration_minutes,
        comment=comment or f"Issued by admin {user_id}",
    )
    return (
        f"✅ ووچر جدید با موفقیت صادر شد:\n\n"
        f"کد: `{voucher.code}`\n"
        f"مدت: {voucher.duration_minutes} دقیقه\n"
        f"توضیحات: {voucher.comment}"
    )


def handle_active_vouchers(
    wifi_service: WiFiService,
    user_id: int,
) -> str:
    if not is_admin(user_id):
        return "⛔ شما دسترسی به دستورات مدیریت را ندارید."

    active = wifi_service.list_vouchers(active_only=True)
    if not active:
        return "ℹ️ در حال حاضر هیچ ووچر فعالی وجود ندارد."

    lines = ["📋 **لیست ووچرهای فعال:**"]
    for v in active:
        used = f"استفاده شده توسط {v.used_by}" if v.used_by else "هنوز استفاده نشده"
        lines.append(f"• `{v.code}` ({v.duration_minutes}m) - {used}")
    return "\n".join(lines)


def handle_status(wifi_service: WiFiService) -> str:
    status = wifi_service.get_system_status()
    return (
        f"📊 **وضعیت سامانه AirboxVIP Coffeenet:**\n\n"
        f"📡 وضعیت ارتباط با روتر: **{status['router_status']}**\n"
        f"🎟️ کل ووچرها: {status['total_vouchers']}\n"
        f"🟢 ووچرهای فعال: {status['active_vouchers']}\n"
        f"👥 نشست‌های فعال: {status['active_sessions']}"
    )
