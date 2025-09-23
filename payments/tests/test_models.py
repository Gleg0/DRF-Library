import unittest
from django.core.validators import MinValueValidator
from django.db import models
from payments.models import Payment


class PaymentModelTestCase(unittest.TestCase):
    def test_status_field_configuration(self):
        field = Payment._meta.get_field("status")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 10)
        self.assertEqual(field.choices, Payment.Status.choices)
        self.assertEqual(field.default, Payment.Status.PENDING)

    def test_type_field_configuration(self):
        field = Payment._meta.get_field("type")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 10)
        self.assertEqual(field.choices, Payment.Type.choices)
        self.assertEqual(field.default, Payment.Type.PAYMENT)

    def test_session_url_field_configuration(self):
        field = Payment._meta.get_field("session_url")
        self.assertIsInstance(field, models.URLField)
        self.assertEqual(field.max_length, 1000)

    def test_session_id_field_configuration(self):
        field = Payment._meta.get_field("session_id")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 255)

    def test_money_to_pay_field_configuration(self):
        field = Payment._meta.get_field("money_to_pay")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 7)
        self.assertEqual(field.decimal_places, 2)
        self.assertTrue(any(isinstance(v, MinValueValidator) for v in field.validators))
        self.assertEqual(field.default, 0.00)

    def test_str_method(self):
        payment = Payment()
        payment.id = 123
        payment.type = Payment.Type.PAYMENT
        payment.status = Payment.Status.PENDING

        self.assertEqual(str(payment), "Payment 123 - PAYMENT - PENDING")
