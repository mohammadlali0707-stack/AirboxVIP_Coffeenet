import logging
from telegram.ext import Application, CommandHandler
from bot.config import config
from bot.services.wifi_service import WiFiService
from bot.handlers.wifi import handle_wifi_request
from bot.handlers.admin import (
    handle_status,
    handle_admin,
    handle_vouchers,
    handle_revoke,
    handle_stats,
    require_admin,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("AirboxVIP-Coffeenet")

wifi_service = WiFiService()


async def start(update, context):
    """Welcome message in Persian"""
    text = (
        "سلام! به ربات وایفای AirboxVIP خوش آمدید.\n\n"
        "دستورات:\n"
        "/wifi - دریافت کد وایفای\n"
        "/status - وضعیت سیستم\n"
        "/help - راهنما"
    )
    await update.message.reply_text(text)


async def wifi_cmd(update, context):
    """Issue a voucher to the user"""
    user_id = str(update.effective_user.id) if update.effective_user else "anonymous"
    reply = handle_wifi_request(wifi_service, user_id=user_id)
    await update.message.reply_text(reply)


async def status_cmd(update, context):
    """Show system status in Persian"""
    reply = handle_status(wifi_service)
    await update.message.reply_text(reply)


@require_admin
async def admin_cmd(update, context):
    """Admin panel menu (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    reply = handle_admin(user_id)
    await update.message.reply_text(reply)


@require_admin
async def vouchers_cmd(update, context):
    """List 10 active vouchers (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    reply = handle_vouchers(wifi_service, user_id)
    await update.message.reply_text(reply)


@require_admin
async def revoke_cmd(update, context):
    """Revoke a voucher by code (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    code = context.args[0] if context.args else ""
    reply = handle_revoke(wifi_service, user_id, code)
    await update.message.reply_text(reply)


@require_admin
async def stats_cmd(update, context):
    """Show admin statistics (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    reply = handle_stats(wifi_service, user_id)
    await update.message.reply_text(reply)


def main():
    app = Application.builder().token(config.bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wifi", wifi_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("vouchers", vouchers_cmd))
    app.add_handler(CommandHandler("revoke", revoke_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.run_polling()


if __name__ == "__main__":
    main()
