from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from base.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingAdminDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list" and not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
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
        return BorrowingSerializer

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsAuthenticated()]
        return [IsAdminOrIfAuthenticatedReadOnly()]
