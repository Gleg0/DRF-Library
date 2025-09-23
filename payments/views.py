from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from base.services.payments_service import StripePaymentService
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentDetailSerializer, PaymentListSerializer


@extend_schema(
    description="""
    API endpoint for retrieving and listing payment records.

    - list: Returns a list of payments. Admin users see all payments; regular users see only their own.
    - retrieve: Returns detailed information about a specific payment.
    - success: Custom action (GET /payments/success) triggered after a successful Stripe payment.
    - cancel`: Custom action (GET /payments/cancel) triggered when a payment is cancelled.
    """
)
class PaymentListRetrieveViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "borrowing__book", "borrowing__user"
        ).order_by("-status")

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return PaymentDetailSerializer

    @extend_schema(
        description="""
        - `success`: Custom action (`GET /payments/success`) triggered after a successful Stripe payment.
        """
    )
    @action(detail=False, methods=["get"])
    def success(self, request: Request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "No session_id provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    "error": (
                        f"This payment was "
                        f"already {payment.status.lower()}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_service = StripePaymentService()

        if payment_service.is_paid(session_id):
            payment.status = Payment.Status.PAID
            payment.save()
            return Response({"message": "Payment successful!"})

        return Response({"message": "Payment not successful!"})

    @extend_schema(
        description="""
        - `cancel`: Custom action (`GET /payments/cancel`) triggered when a payment is cancelled.
        """
    )
    @action(detail=False, methods=["get"])
    def cancel(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "No session_id provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    "error": (
                        f"This payment was "
                        f"already {payment.status.lower()}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            payment.status = Payment.Status.CANCELLED
            payment.save()
            Borrowing.objects.filter(id=payment.borrowing_id).update(
                actual_return_date=timezone.now()
            )

            payment_service = StripePaymentService()
            payment_service.mark_session_as_expired(session_id)

            Book.objects.filter(id=payment.borrowing.book_id).update(
                inventory=F("inventory") + 1
            )

        return Response({"message": "Payment was cancelled."})
