import unittest
from django.apps import apps
from payments.apps import PaymentsConfig


class PaymentsConfigTestCase(unittest.TestCase):
    def test_payments_config_name(self):
        """PaymentsConfig should use the correct app label."""
        self.assertEqual(PaymentsConfig.name, "payments")

    def test_payments_config_loaded(self):
        """PaymentsConfig should be discoverable in Django apps registry."""
        config = apps.get_app_config("payments")
        self.assertIsInstance(config, PaymentsConfig)
        self.assertEqual(config.name, "payments")

    def test_default_auto_field(self):
        """PaymentsConfig should use BigAutoField as default_auto_field."""
        self.assertEqual(
            PaymentsConfig.default_auto_field,
            "django.db.models.BigAutoField"
        )
