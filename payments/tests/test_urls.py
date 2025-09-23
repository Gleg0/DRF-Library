import unittest

from payments import urls


class PaymentsUrlsTestCase(unittest.TestCase):
    def test_app_name(self):
        self.assertEqual(urls.app_name, "payments")
