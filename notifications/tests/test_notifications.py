from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone

from books.models import Book
from borrowings.models import Borrowing
from notifications import tasks
from payments.models import Payment
from users.models import User


class BorrowingSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", password="pass")
        self.book = Book.objects.create(
            title="TestBook", daily_fee=10, inventory=5
        )

    @patch("notifications.tasks.notify_borrowings.delay")
    @patch(
        "base.services.payments_service.StripePaymentService.create_payment_session"
    )
    def test_create_notify(self, mock_stripe, mock_notify):
        mock_stripe.return_value = MagicMock(
            id="sess_123", url="http://stripe"
        )

        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return=timezone.now().date() + timezone.timedelta(days=3),
        )

        mock_notify.assert_called_once_with(
            borrowing_id=borrowing.id,
            user_name=self.user.email,
            book_title=self.book.title,
            expected_return=borrowing.expected_return,
        )


class PaymentSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", password="pass")
        self.book = Book.objects.create(title="Book", daily_fee=5, inventory=1)
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return=timezone.now().date() + timezone.timedelta(days=1),
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            money_to_pay=5,
            session_url="url",
            session_id="id",
        )

    @patch("notifications.tasks.notify_payment.delay")
    def test_payment_paid_triggers_notify(self, mock_notify):
        self.payment.status = Payment.Status.PAID
        self.payment.save()

        mock_notify.assert_called_once_with(
            payment_id=self.payment.id,
            payment_type=self.payment.type,
            money_to_pay=self.payment.money_to_pay,
        )


class NotificationTasksTests(TestCase):

    @patch("notifications.tasks.send_message")
    def test_notify_borrowings(self, mock_send):
        tasks.notify_borrowings.run(
            borrowing_id=1,
            user_name="Alice",
            book_title="Book 1",
            expected_return="2025-09-01",
        )
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        self.assertIn("✨ New Borrowing", args[0])

    @patch("notifications.tasks.send_message")
    def test_notify_payment(self, mock_send):
        tasks.notify_payment.run(
            payment_id=42,
            payment_type="card",
            money_to_pay="150",
        )
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        self.assertIn("💳 Payment", args[0])

    @patch("notifications.tasks.send_message")
    def test_notify_daily(self, mock_send):
        tasks.notify_daily.run()
        mock_send.assert_called_once()
