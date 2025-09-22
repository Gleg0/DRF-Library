from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from base.payments_service import StripePaymentService
from books.models import Book
from payments.models import Payment
from payments.serializers import PaymentDetailSerializer, PaymentListSerializer


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

    @action(detail=False, methods=["get"])
    def success(self, request: Request):
        """
        Redirect after successful payment
        """
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "No session_id provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        payment_service = StripePaymentService()

        if payment_service.is_paid(session_id):
            payment.status = Payment.Status.PAID
            payment.save()
            return Response({"message": "Payment successful!"})

        return Response({"message": "Payment not successful!"})

    @action(detail=False, methods=["get"])
    def cancel(self, request):
        """
        Redirect if payment was cancelled
        """
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "No session_id provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = get_object_or_404(Payment, session_id=session_id)

        if payment.status == Payment.Status.CANCELLED:
            return Response(
                {"message": "Payment was already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            payment.status = Payment.Status.CANCELLED
            payment.save()

            Book.objects.filter(id=payment.borrowing.book_id).update(
                inventory=F("inventory") + 1
            )

        return Response({"message": "Payment was cancelled."})
