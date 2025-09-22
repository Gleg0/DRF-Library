from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from base.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.filters import BorrowingAdminFilter, BorrowingFilter
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingAdminDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
    BorrowingSerializer,
)
from borrowings.services.services import BorrowingService


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    filterset_class = BorrowingAdminFilter

    @action(detail=True, methods=["post"], url_path="return")
    def borrowing_return(self, request, pk=None):
        borrowing = self.get_object()
        borrowing = BorrowingService.book_return(borrowing)
        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list" and not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            self.filterset_class = BorrowingFilter

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            if not self.request.user.is_staff:
                return BorrowingListSerializer
            return BorrowingAdminListSerializer
        elif self.action == "retrieve":
            if not self.request.user.is_staff:
                return BorrowingDetailSerializer
            return BorrowingAdminDetailSerializer
        elif self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "borrowing_return":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def get_permissions(self):
        if self.action in ["list", "create", "borrowing_return"]:
            return [IsAuthenticated()]
        return [IsAdminOrIfAuthenticatedReadOnly()]
