import unittest
from django.contrib import admin
from payments.admin import PaymentAdmin
from payments.models import Payment


class PaymentAdminTestCase(unittest.TestCase):
    def test_payment_is_registered_in_admin(self):
        """Check that Payment model is registered in admin site."""
        self.assertIn(Payment, admin.site._registry)

    def test_payment_admin_list_display(self):
        """Check that PaymentAdmin has the correct list_display fields."""
        payment_admin = PaymentAdmin(Payment, admin.site)
        expected_fields = (
            "borrowing",
            "money_to_pay",
            "status",
            "type",
            "session_url",
            "session_id",
        )
        self.assertEqual(payment_admin.list_display, expected_fields)
