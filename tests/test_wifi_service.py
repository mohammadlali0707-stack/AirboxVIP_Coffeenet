import unittest
from bot.models.voucher import Voucher
from bot.services.router_client import MockRouterClient
from bot.services.wifi_service import WiFiService
from bot.handlers.admin import handle_issue, handle_revoke, handle_active_vouchers, handle_status
from bot.handlers.wifi import handle_wifi_request
from bot.config import config


class TestVoucherModel(unittest.TestCase):
    def test_voucher_generation(self):
        v = Voucher.generate(duration_minutes=30, upload_limit_mb=100, download_limit_mb=200)
        self.assertEqual(len(v.code), 6)
        self.assertEqual(v.duration_minutes, 30)
        self.assertEqual(v.upload_limit_mb, 100)
        self.assertEqual(v.download_limit_mb, 200)
        self.assertTrue(v.is_active)
        self.assertIsNone(v.used_by)

    def test_voucher_serialization(self):
        v = Voucher.generate()
        d = v.to_dict()
        self.assertIn("code", d)
        self.assertIn("duration_minutes", d)
        self.assertTrue(d["is_active"])


class TestWiFiService(unittest.TestCase):
    def setUp(self):
        self.mock_router = MockRouterClient()
        self.service = WiFiService(router_client=self.mock_router)

    def test_issue_and_retrieve_voucher(self):
        v = self.service.issue_voucher(duration_minutes=45, comment="Test table")
        self.assertEqual(v.duration_minutes, 45)
        self.assertIn(v.code, self.mock_router.users)

        retrieved = self.service.get_voucher(v.code)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.code, v.code)

    def test_redeem_voucher(self):
        v = self.service.issue_voucher()
        success = self.service.redeem_voucher(v.code, user_id="user_99")
        self.assertTrue(success)
        self.assertEqual(v.used_by, "user_99")
        self.assertIsNotNone(v.used_at)

        # Cannot redeem again
        again = self.service.redeem_voucher(v.code, user_id="user_100")
        self.assertFalse(again)

    def test_revoke_voucher(self):
        v = self.service.issue_voucher()
        self.assertTrue(v.is_active)
        self.assertIn(v.code, self.mock_router.users)

        success = self.service.revoke_voucher(v.code)
        self.assertTrue(success)
        self.assertFalse(v.is_active)
        self.assertNotIn(v.code, self.mock_router.users)

    def test_system_status(self):
        status = self.service.get_system_status()
        self.assertEqual(status["router_status"], "Online")
        self.assertEqual(status["total_vouchers"], 0)

        self.service.issue_voucher()
        status = self.service.get_system_status()
        self.assertEqual(status["total_vouchers"], 1)
        self.assertEqual(status["active_vouchers"], 1)


class TestHandlers(unittest.TestCase):
    def setUp(self):
        self.mock_router = MockRouterClient()
        self.service = WiFiService(router_client=self.mock_router)
        config.admin_chat_ids = [999]

    def test_wifi_request_handler(self):
        msg = handle_wifi_request(self.service, user_id="test_user")
        self.assertIn("کد وای‌فای اختصاصی شما آماده است", msg)
        self.assertEqual(len(self.service.list_vouchers()), 1)

    def test_admin_issue_forbidden_for_regular_user(self):
        res = handle_issue(self.service, user_id=111)
        self.assertIn("دسترسی", res)

    def test_admin_issue_allowed_for_admin(self):
        res = handle_issue(self.service, user_id=999, duration_minutes=120)
        self.assertIn("ووچر جدید با موفقیت صادر شد", res)
        self.assertIn("120 دقیقه", res)

    def test_admin_revoke(self):
        v = self.service.issue_voucher()
        res = handle_revoke(self.service, user_id=999, code=v.code)
        self.assertIn("غیرفعال شد", res)
        self.assertFalse(v.is_active)

    def test_status_handler(self):
        msg = handle_status(self.service)
        self.assertIn("وضعیت سامانه AirboxVIP Coffeenet", msg)


if __name__ == "__main__":
    unittest.main()
