import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.main import start, wifi_cmd, status_cmd, main
from bot.config import config


class TestBotCommands(unittest.IsolatedAsyncioTestCase):
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

    async def test_wifi_command(self):
        update = MagicMock()
        update.effective_user.id = 55555
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

    @patch("bot.main.Application")
    def test_main_registration(self, mock_app_cls):
        mock_builder = MagicMock()
        mock_app_cls.builder.return_value = mock_builder
        mock_builder.token.return_value = mock_builder
        mock_app = MagicMock()
        mock_builder.build.return_value = mock_app

        main()

        mock_app_cls.builder.assert_called_once()
        mock_builder.token.assert_called_once_with(config.bot_token)
        mock_builder.build.assert_called_once()

        # Check that 4 CommandHandlers were registered
        self.assertEqual(mock_app.add_handler.call_count, 4)
        registered_commands = [
            list(call.args[0].commands)[0]
            for call in mock_app.add_handler.call_args_list
        ]
        self.assertIn("start", registered_commands)
        self.assertIn("wifi", registered_commands)
        self.assertIn("status", registered_commands)
        self.assertIn("help", registered_commands)
        mock_app.run_polling.assert_called_once()


if __name__ == "__main__":
    unittest.main()
