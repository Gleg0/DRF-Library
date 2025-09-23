import unittest
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import AnonymousUser, User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from payments.views import PaymentListRetrieveViewSet
from payments.models import Payment


factory = APIRequestFactory()


class PaymentViewSetActionsTestCase(unittest.TestCase):
    def setUp(self):
        self.success_view = PaymentListRetrieveViewSet.as_view({"get": "success"})
        self.cancel_view = PaymentListRetrieveViewSet.as_view({"get": "cancel"})
        self.user = User(username="testuser", email="test@example.com")

    @patch("payments.views.get_object_or_404")
    @patch("payments.views.StripePaymentService")
    def test_success_payment_paid(self, mock_service, mock_get_object):
        request = factory.get("/payments/success/?session_id=abc123")
        force_authenticate(request, user=self.user)

        # fake Payment object
        payment = MagicMock()
        payment.status = Payment.Status.PENDING
        mock_get_object.return_value = payment

        # fake Stripe service
        service_instance = mock_service.return_value
        service_instance.is_paid.return_value = True

        response = self.success_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Payment successful!"})
        payment.save.assert_called_once()

    @patch("payments.views.get_object_or_404")
    @patch("payments.views.StripePaymentService")
    def test_success_payment_not_paid(self, mock_service, mock_get_object):
        request = factory.get("/payments/success/?session_id=abc123")
        force_authenticate(request, user=self.user)

        payment = MagicMock()
        payment.status = Payment.Status.PENDING
        mock_get_object.return_value = payment

        service_instance = mock_service.return_value
        service_instance.is_paid.return_value = False

        response = self.success_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Payment not successful!"})

    @patch("payments.views.get_object_or_404")
    @patch("payments.views.Borrowing.objects.filter")
    @patch("payments.views.Book.objects.filter")
    @patch("payments.views.StripePaymentService")
    def test_cancel_payment(self, mock_service, mock_book_filter, mock_borrowing_filter, mock_get_object):
        request = factory.get("/payments/cancel/?session_id=xyz789")
        force_authenticate(request, user=self.user)

        payment = MagicMock()
        payment.status = Payment.Status.PENDING
        payment.borrowing_id = 1
        payment.borrowing.book_id = 2
        mock_get_object.return_value = payment

        response = self.cancel_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Payment was cancelled."})

        payment.save.assert_called_once()
        mock_borrowing_filter.assert_called_once_with(id=1)
        mock_book_filter.assert_called_once_with(id=2)
        mock_service.return_value.mark_session_as_expired.assert_called_once_with("xyz789")
