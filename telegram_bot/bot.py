import logging
import os
import sys
from pathlib import Path

# Ensure repo root is in sys.path so modules can be imported
_repo_root = str(Path(__file__).resolve().parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import telegram_bot.config as bot_config
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
logger = logging.getLogger("AirboxVIP-TelegramBot")

wifi_service = WiFiService()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message in Persian"""
    text = (
        "سلام! به ربات وایفای AirboxVIP خوش آمدید.\n\n"
        "دستورات:\n"
        "/wifi - دریافت کد وایفای\n"
        "/status - وضعیت سیستم\n"
        "/help - راهنما"
    )
    await update.message.reply_text(text)


async def wifi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Issue a voucher to the user"""
    user_id = str(update.effective_user.id) if update.effective_user else "anonymous"
    reply = handle_wifi_request(wifi_service, user_id=user_id)
    await update.message.reply_text(reply)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system status in Persian"""
    reply = handle_status(wifi_service)
    await update.message.reply_text(reply)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message in Persian"""
    await start(update, context)


@require_admin
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel menu (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    reply = handle_admin(user_id)
    await update.message.reply_text(reply)


@require_admin
async def vouchers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List 10 active vouchers (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    reply = handle_vouchers(wifi_service, user_id)
    await update.message.reply_text(reply)


@require_admin
async def revoke_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Revoke a voucher by code (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    code = context.args[0] if context.args else ""
    reply = handle_revoke(wifi_service, user_id, code)
    await update.message.reply_text(reply)


@require_admin
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin statistics (admin only)"""
    user_id = update.effective_user.id if update.effective_user else None
    reply = handle_stats(wifi_service, user_id)
    await update.message.reply_text(reply)


def create_application() -> Application:
    """Build Application and register all command handlers."""
    token = (
        getattr(bot_config, "TELEGRAM_TOKEN", None)
        or getattr(bot_config, "TELEGRAM_BOT_TOKEN", None)
        or getattr(bot_config.config, "bot_token", None)
        or os.getenv("TELEGRAM_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("BOT_TOKEN", "")
    )
    if not token:
        logger.warning("TELEGRAM_TOKEN is not set in environment or .env file.")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wifi", wifi_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("vouchers", vouchers_cmd))
    app.add_handler(CommandHandler("revoke", revoke_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    return app


def main():
    app = create_application()
    logger.info("AirboxVIP Coffeenet bot starting polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
