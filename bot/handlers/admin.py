from typing import Optional
from bot.services.wifi_service import WiFiService
from bot.config import config


def handle_issue(
    wifi_service: WiFiService,
    user_id: int,
    duration_minutes: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    if not config.is_admin(user_id):
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


def handle_revoke(
    wifi_service: WiFiService,
    user_id: int,
    code: str,
) -> str:
    if not config.is_admin(user_id):
        return "⛔ شما دسترسی به دستورات مدیریت را ندارید."

    if wifi_service.revoke_voucher(code):
        return f"✅ ووچر `{code}` غیرفعال شد."
    return f"❌ ووچر با کد `{code}` یافت نشد."


def handle_active_vouchers(
    wifi_service: WiFiService,
    user_id: int,
) -> str:
    if not config.is_admin(user_id):
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
