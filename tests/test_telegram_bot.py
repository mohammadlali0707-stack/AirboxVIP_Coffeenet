import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import telegram_bot.config as bot_config
from telegram_bot.bot import (
    start,
    wifi_cmd,
    status_cmd,
    help_cmd,
    admin_cmd,
    vouchers_cmd,
    revoke_cmd,
    stats_cmd,
    create_application,
    main,
)


class TestTelegramBotCommands(unittest.IsolatedAsyncioTestCase):
    async def test_start_command(self):
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await start(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("سلام! به ربات وایفای AirboxVIP خوش آمدید.", text)
        self.assertIn("/wifi", text)
        self.assertIn("/status", text)
        self.assertIn("/help", text)

    async def test_help_command(self):
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await help_cmd(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("سلام! به ربات وایفای AirboxVIP خوش آمدید.", text)
        self.assertIn("/wifi", text)
        self.assertIn("/status", text)
        self.assertIn("/help", text)

    async def test_wifi_command(self):
        update = MagicMock()
        update.effective_user.id = 77777
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await wifi_cmd(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("کد وای‌فای اختصاصی شما آماده است", text)
        self.assertIn("کد اتصال", text)

    async def test_status_command(self):
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await status_cmd(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("وضعیت سامانه AirboxVIP Coffeenet", text)
        self.assertIn("وضعیت ارتباط با روتر", text)

    async def test_admin_cmd_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await admin_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    @patch("telegram_bot.bot.Application")
    def test_application_registration(self, mock_app_cls):
        mock_builder = MagicMock()
        mock_app_cls.builder.return_value = mock_builder
        mock_builder.token.return_value = mock_builder
        mock_app = MagicMock()
        mock_builder.build.return_value = mock_app

        app = create_application()

        mock_app_cls.builder.assert_called_once()
        mock_builder.build.assert_called_once()

        self.assertEqual(mock_app.add_handler.call_count, 8)
        registered_commands = [
            list(call.args[0].commands)[0]
            for call in mock_app.add_handler.call_args_list
        ]
        self.assertIn("start", registered_commands)
        self.assertIn("wifi", registered_commands)
        self.assertIn("status", registered_commands)
        self.assertIn("help", registered_commands)
        self.assertIn("admin", registered_commands)
        self.assertIn("vouchers", registered_commands)
        self.assertIn("revoke", registered_commands)
        self.assertIn("stats", registered_commands)

    @patch("telegram_bot.bot.create_application")
    def test_main(self, mock_create):
        mock_app = MagicMock()
        mock_create.return_value = mock_app

        main()

        mock_create.assert_called_once()
        mock_app.run_polling.assert_called_once()


class TestTelegramBotConfig(unittest.TestCase):
    def test_config_token_resolution(self):
        with patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token_123"}, clear=True):
            cfg = bot_config.Config()
            self.assertEqual(cfg.bot_token, "test_token_123")

    def test_config_admin_check(self):
        cfg = bot_config.Config()
        cfg.admin_user_ids = [111, 222]
        self.assertTrue(cfg.is_admin(111))
        self.assertTrue(cfg.is_admin("222"))
        self.assertFalse(cfg.is_admin(333))
        self.assertFalse(cfg.is_admin(None))


if __name__ == "__main__":
    unittest.main()
