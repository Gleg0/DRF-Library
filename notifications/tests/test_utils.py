from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from notifications.services import utils
from users.models import User


class UtilsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@test.com", password="pass")
        self.book = Book.objects.create(
            title="Book", daily_fee=10, inventory=1
        )

    def test_borrowings_with_overdue_not_found(self):
        text = utils.borrowings_with_overdue()
        self.assertEqual(text, "📢 Check completed 📢\n" "No records found")

    @patch(
        "base.services.payments_service.StripePaymentService.create_payment_session"
    )
    def test_borrowings_with_overdue_found(self, mock_stripe):
        mock_stripe.return_value = MagicMock(
            id="sess_123", url="http://stripe"
        )

        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=date.today() - timedelta(days=5),
            expected_return=date.today() - timedelta(days=2),
        )

        text = utils.borrowings_with_overdue()
        self.assertIn("📢 Outdate borrowings:", text)
        self.assertIn(str(borrowing.id), text)
        self.assertIn(self.user.email, text)
        self.assertIn(self.book.title, text)

    def test_new_borrowing_format(self):
        text = utils.new_borrowing(
            borrowing_id=1,
            user_name="test@test.com",
            book_title="SomeBook",
            expected_return="2025-09-30",
        )
        self.assertIn("✨ New Borrowing №1", text)
        self.assertIn("SomeBook", text)
        self.assertIn("2025-09-30", text)

    def test_payment_success_format(self):
        text = utils.payment_success(
            payment_id=42,
            payment_type="FINE",
            money_to_pay=150,
        )
        self.assertIn("💳 Payment №42", text)
        self.assertIn("FINE", text)
        self.assertIn("150", text)
