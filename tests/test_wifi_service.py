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
        self.service = WiFiService(router_client=self.mock_router, db_path=":memory:")

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
        self.service = WiFiService(router_client=self.mock_router, db_path=":memory:")
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


class TestDatabase(unittest.TestCase):
    def setUp(self):
        from bot.database import Database
        self.db = Database(db_path=":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_and_get_voucher(self):
        v = Voucher.generate(duration_minutes=30, upload_limit_mb=100, download_limit_mb=200, comment="test")
        self.db.add_voucher(v)

        retrieved = self.db.get_voucher(v.code)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.code, v.code)
        self.assertEqual(retrieved.duration_minutes, 30)
        self.assertEqual(retrieved.upload_limit_mb, 100)
        self.assertEqual(retrieved.download_limit_mb, 200)
        self.assertTrue(retrieved.is_active)
        self.assertEqual(retrieved.comment, "test")

    def test_update_voucher(self):
        v = Voucher.generate(duration_minutes=30)
        self.db.add_voucher(v)

        v.is_active = False
        v.used_by = "12345"
        v.used_at = "2026-09-07T12:00:00"
        updated = self.db.update_voucher(v)
        self.assertTrue(updated)

        retrieved = self.db.get_voucher(v.code)
        self.assertFalse(retrieved.is_active)
        self.assertEqual(retrieved.used_by, "12345")
        self.assertEqual(retrieved.used_at, "2026-09-07T12:00:00")

    def test_list_and_count_vouchers(self):
        self.assertEqual(self.db.count_vouchers(), 0)
        v1 = Voucher.generate(comment="v1")
        v2 = Voucher.generate(comment="v2")
        self.db.add_voucher(v1)
        self.db.add_voucher(v2)

        self.assertEqual(self.db.count_vouchers(), 2)
        self.assertEqual(self.db.count_vouchers(active_only=True), 2)
        self.assertEqual(len(self.db.list_vouchers()), 2)

        v1.is_active = False
        self.db.update_voucher(v1)
        self.assertEqual(self.db.count_vouchers(active_only=True), 1)
        self.assertEqual(len(self.db.list_vouchers(active_only=True)), 1)


class TestPersistence(unittest.TestCase):
    def test_persistence_across_service_instances(self):
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            # First service instance creates and issues voucher
            router1 = MockRouterClient()
            service1 = WiFiService(router_client=router1, db_path=db_path)
            v = service1.issue_voucher(duration_minutes=90, comment="Persistence test")
            code = v.code
            service1.db.close()

            # Second service instance opens the same DB file and retrieves voucher
            router2 = MockRouterClient()
            service2 = WiFiService(router_client=router2, db_path=db_path)
            retrieved = service2.get_voucher(code)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.code, code)
            self.assertEqual(retrieved.duration_minutes, 90)
            self.assertEqual(retrieved.comment, "Persistence test")

            # Redeem voucher in service2
            self.assertTrue(service2.redeem_voucher(code, user_id="user_persistent"))
            service2.db.close()

            # Third service instance verifies redemption persisted
            service3 = WiFiService(router_client=MockRouterClient(), db_path=db_path)
            v3 = service3.get_voucher(code)
            self.assertEqual(v3.used_by, "user_persistent")
            self.assertIsNotNone(v3.used_at)
            service3.db.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == "__main__":
    unittest.main()

