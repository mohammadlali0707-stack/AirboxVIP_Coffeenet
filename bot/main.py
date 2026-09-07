import sys
import logging
from bot.config import config
from bot.services.wifi_service import WiFiService
from bot.handlers.common import WELCOME_MESSAGE, HELP_MESSAGE
from bot.handlers.wifi import handle_wifi_request
from bot.handlers.admin import (
    handle_issue,
    handle_revoke,
    handle_active_vouchers,
    handle_status,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("AirboxVIP-Coffeenet")


def run_cli_demo():
    """Interactive / demo mode for local testing without Telegram API."""
    print("========================================")
    print("AirboxVIP-Coffeenet Telegram Bot (Demo)")
    print("========================================")
    wifi_service = WiFiService()
    print("System status:")
    print(handle_status(wifi_service))
    print("\nGenerating sample voucher for customer...")
    msg = handle_wifi_request(wifi_service, user_id="12345", comment="Table 4")
    print(msg)
    print("\nUpdated status:")
    print(handle_status(wifi_service))
    print("========================================")
    return 0


def run_telegram_bot():
    """Main Telegram bot runner using python-telegram-bot."""
    try:
        from telegram import Update
        from telegram.ext import (
            ApplicationBuilder,
            CommandHandler,
            ContextTypes,
        )
    except ImportError:
        logger.error(
            "python-telegram-bot is not installed. Please run: pip install -r requirements.txt"
        )
        return 1

    if not config.bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment or .env file.")
        return 1

    wifi_service = WiFiService()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")

    async def wifi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        reply = handle_wifi_request(wifi_service, user_id)
        await update.message.reply_text(reply, parse_mode="Markdown")

    async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply = handle_status(wifi_service)
        await update.message.reply_text(reply, parse_mode="Markdown")

    async def issue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        minutes = None
        if context.args and context.args[0].isdigit():
            minutes = int(context.args[0])
        reply = handle_issue(wifi_service, user_id, duration_minutes=minutes)
        await update.message.reply_text(reply, parse_mode="Markdown")

    async def active_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        reply = handle_active_vouchers(wifi_service, user_id)
        await update.message.reply_text(reply, parse_mode="Markdown")

    async def revoke_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not context.args:
            await update.message.reply_text("فرمت دستور: /revoke <کد_ووچر>")
            return
        code = context.args[0]
        reply = handle_revoke(wifi_service, user_id, code)
        await update.message.reply_text(reply, parse_mode="Markdown")

    app = ApplicationBuilder().token(config.bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("wifi", wifi_cmd))
    app.add_handler(CommandHandler("voucher", wifi_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("issue", issue_cmd))
    app.add_handler(CommandHandler("active", active_cmd))
    app.add_handler(CommandHandler("revoke", revoke_cmd))

    logger.info("AirboxVIP Coffeenet bot starting polling...")
    app.run_polling()
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        sys.exit(run_cli_demo())
    elif not config.bot_token:
        logger.warning("No TELEGRAM_BOT_TOKEN provided. Running in demo mode.")
        sys.exit(run_cli_demo())
    else:
        sys.exit(run_telegram_bot())
