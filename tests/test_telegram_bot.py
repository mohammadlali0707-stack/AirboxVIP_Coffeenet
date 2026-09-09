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
        update.effective_chat.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await admin_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_admin_cmd_success(self):
        bot_config.ADMIN_USER_IDS = [12345]
        bot_config.ADMIN_CHAT_IDS = [12345]
        bot_config.config.admin_user_ids = [12345]
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await admin_cmd(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("پنل مدیریت", text)

    async def test_vouchers_cmd_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.effective_chat.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await vouchers_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_vouchers_cmd_success(self):
        bot_config.ADMIN_USER_IDS = [12345]
        bot_config.ADMIN_CHAT_IDS = [12345]
        bot_config.config.admin_user_ids = [12345]
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = []

        await vouchers_cmd(update, context)
        update.message.reply_text.assert_called_once()

    async def test_revoke_cmd_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.effective_chat.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = ["SOMECODE"]

        await revoke_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_revoke_cmd_success(self):
        bot_config.ADMIN_USER_IDS = [12345]
        bot_config.ADMIN_CHAT_IDS = [12345]
        bot_config.config.admin_user_ids = [12345]
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = ["NONEXISTENT"]

        await revoke_cmd(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("کد یافت نشد", text)

    async def test_stats_cmd_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.effective_chat.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await stats_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_stats_cmd_success(self):
        bot_config.ADMIN_USER_IDS = [12345]
        bot_config.ADMIN_CHAT_IDS = [12345]
        bot_config.config.admin_user_ids = [12345]
        update = MagicMock()
        update.effective_user.id = 12345
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await stats_cmd(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("آمار سامانه AirboxVIP", text)

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
        self.assertEqual(cfg.admin_chat_ids, [111, 222])
        self.assertEqual(cfg.ADMIN_CHAT_IDS, [111, 222])

    def test_module_is_admin_check(self):
        bot_config.ADMIN_CHAT_IDS = [555, 666]
        bot_config.ADMIN_USER_IDS = [555, 666]
        self.assertTrue(bot_config.is_admin(555))
        self.assertTrue(bot_config.is_admin("666"))
        self.assertFalse(bot_config.is_admin(777))
        self.assertFalse(bot_config.is_admin(None))


class TestTelegramBotDatabase(unittest.TestCase):
    def setUp(self):
        import tempfile
        import telegram_bot.database as db
        self.db = db
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.test_db = self.tmp.name
        self.tmp.close()
        self.db.init_db(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except Exception:
                pass

    def test_add_and_get_voucher(self):
        code = self.db.add_voucher("TEST01", duration_minutes=30, db_path=self.test_db)
        self.assertEqual(code, "TEST01")
        v = self.db.get_voucher("TEST01", db_path=self.test_db)
        self.assertIsNotNone(v)
        self.assertEqual(v["code"], "TEST01")
        self.assertEqual(v["duration_minutes"], 30)
        self.assertEqual(v["is_active"], 1)

    def test_list_and_all_vouchers(self):
        self.db.add_voucher("CODE1", db_path=self.test_db)
        self.db.add_voucher("CODE2", db_path=self.test_db)
        vouchers = self.db.list_vouchers(db_path=self.test_db)
        self.assertEqual(len(vouchers), 2)
        all_vouchers = self.db.get_all_vouchers(db_path=self.test_db)
        self.assertEqual(len(all_vouchers), 2)

    def test_revoke_voucher(self):
        self.db.add_voucher("REV01", db_path=self.test_db)
        self.assertTrue(self.db.revoke_voucher("REV01", db_path=self.test_db))
        v = self.db.get_voucher("REV01", db_path=self.test_db)
        self.assertEqual(v["is_active"], 0)
        self.assertFalse(self.db.revoke_voucher("NONEXISTENT", db_path=self.test_db))

    def test_voucher_stats(self):
        self.db.add_voucher("STAT1", db_path=self.test_db)
        self.db.add_voucher("STAT2", db_path=self.test_db)
        self.db.revoke_voucher("STAT1", db_path=self.test_db)

        stats = self.db.get_voucher_stats(db_path=self.test_db)
        self.assertEqual(stats["total_vouchers"], 2)
        self.assertEqual(stats["active_vouchers"], 1)
        self.assertEqual(stats["today_vouchers"], 2)

    def test_delete_and_clear_vouchers(self):
        self.db.add_voucher("DEL1", db_path=self.test_db)
        self.assertTrue(self.db.delete_voucher("DEL1", db_path=self.test_db))
        self.assertIsNone(self.db.get_voucher("DEL1", db_path=self.test_db))
        self.db.add_voucher("DEL2", db_path=self.test_db)
        self.db.clear_vouchers(db_path=self.test_db)
        self.assertEqual(self.db.count_vouchers(db_path=self.test_db), 0)


if __name__ == "__main__":
    unittest.main()
