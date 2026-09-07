from bot.services.wifi_service import WiFiService


def format_voucher_message(voucher) -> str:
    return (
        f"🎟️ **کد وای‌فای اختصاصی شما آماده است!**\n\n"
        f"🔑 **کد اتصال:** `{voucher.code}`\n"
        f"⏳ **مدت اعتبار:** {voucher.duration_minutes} دقیقه\n"
        f"📊 **حجم مجاز:** {voucher.download_limit_mb} مگابایت دریافت / {voucher.upload_limit_mb} مگابایت ارسال\n\n"
        f"📱 **نحوه استفاده:**\n"
        f"1. به شبکه وای‌فای کافه متصل شوید.\n"
        f"2. در صفحه ورود، کد بالا را به عنوان نام کاربری و رمز عبور وارد کنید."
    )


def handle_wifi_request(wifi_service: WiFiService, user_id: str, comment: str = None) -> str:
    voucher = wifi_service.issue_voucher(comment=comment or f"user:{user_id}")
    wifi_service.redeem_voucher(voucher.code, user_id)
    return format_voucher_message(voucher)
