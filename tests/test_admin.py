import unittest
from unittest.mock import AsyncMock, MagicMock
from bot.config import config
from bot.services.wifi_service import WiFiService
from bot.services.router_client import MockRouterClient
from bot.handlers.admin import (
    is_admin,
    require_admin,
    handle_admin,
    handle_vouchers,
    handle_revoke,
    handle_stats,
)
from bot.main import admin_cmd, vouchers_cmd, revoke_cmd, stats_cmd


class TestAdminHandlers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_router = MockRouterClient()
        self.service = WiFiService(router_client=self.mock_router, db_path=":memory:")
        config.admin_user_ids = [12345, 67890]

    def test_is_admin(self):
        self.assertTrue(is_admin(12345))
        self.assertTrue(is_admin("12345"))
        self.assertFalse(is_admin(99999))
        self.assertFalse(is_admin("invalid"))
        self.assertFalse(is_admin(None))

    def test_handle_admin_forbidden(self):
        res = handle_admin(99999)
        self.assertEqual(res, "⛔ دسترسی ندارید")

    def test_handle_admin_success(self):
        res = handle_admin(12345)
        self.assertIn("پنل مدیریت", res)
        self.assertIn("/admin", res)
        self.assertIn("/vouchers", res)
        self.assertIn("/revoke", res)
        self.assertIn("/stats", res)

    def test_handle_vouchers_forbidden(self):
        res = handle_vouchers(self.service, user_id=99999)
        self.assertEqual(res, "⛔ دسترسی ندارید")

    def test_handle_vouchers_empty(self):
        res = handle_vouchers(self.service, user_id=12345)
        self.assertEqual(res, "هیچ کد فعالی وجود ندارد")

    def test_handle_vouchers_with_data(self):
        v1 = self.service.issue_voucher(duration_minutes=30, comment="User 1")
        self.service.redeem_voucher(v1.code, user_id="cust101")
        v2 = self.service.issue_voucher(duration_minutes=60, comment="User 2")

        res = handle_vouchers(self.service, user_id=12345)
        self.assertIn("code | duration | used_by | created_at", res)
        self.assertIn(v1.code, res)
        self.assertIn(v2.code, res)
        self.assertIn("cust101", res)

    def test_handle_revoke_forbidden(self):
        res = handle_revoke(self.service, user_id=99999, code="TEST01")
        self.assertEqual(res, "⛔ دسترسی ندارید")

    def test_handle_revoke_not_found(self):
        res = handle_revoke(self.service, user_id=12345, code="NONEXISTENT")
        self.assertIn("کد یافت نشد", res)

    def test_handle_revoke_success(self):
        v = self.service.issue_voucher(duration_minutes=45)
        self.assertTrue(v.is_active)
        res = handle_revoke(self.service, user_id=12345, code=v.code)
        self.assertIn(f"✅ کد `{v.code}` غیرفعال شد", res)
        v_check = self.service.get_voucher(v.code)
        self.assertFalse(v_check.is_active)

    def test_handle_stats_forbidden(self):
        res = handle_stats(self.service, user_id=99999)
        self.assertEqual(res, "⛔ دسترسی ندارید")

    def test_handle_stats_success(self):
        self.service.issue_voucher()
        res = handle_stats(self.service, user_id=12345)
        self.assertIn("آمار سامانه AirboxVIP", res)
        self.assertIn("کل ووچرهای امروز", res)
        self.assertIn("ووچرهای فعال اکنون", res)
        self.assertIn("وضعیت روتر", res)

    async def test_admin_cmd_async_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await admin_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_admin_cmd_async_success(self):
        update = MagicMock()
        update.effective_user.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await admin_cmd(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("پنل مدیریت", text)

    async def test_vouchers_cmd_async_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await vouchers_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_revoke_cmd_async_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.args = ["SOMECODE"]

        await revoke_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")

    async def test_stats_cmd_async_forbidden(self):
        update = MagicMock()
        update.effective_user.id = 99999
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        await stats_cmd(update, context)
        update.message.reply_text.assert_called_once_with("⛔ دسترسی ندارید")


if __name__ == "__main__":
    unittest.main()
