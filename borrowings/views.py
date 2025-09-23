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
    """
    API endpoint for managing borrowings.

    - `list`: Returns a filtered list of borrowings. Admin users see all records with `BorrowingAdminFilter`; regular users see only their own borrowings with `BorrowingFilter`.
    - `retrieve`: Returns detailed information about a specific borrowing. Admins receive extended data via `BorrowingAdminDetailSerializer`.
    - `create`: Allows authenticated users to initiate a borrowing. The borrowing is created using `BorrowingService.create_borrowing`.
    - `borrowing_return`: Custom action (`POST /borrowings/{id}/return`) to mark a borrowing as returned. Updates book inventory and borrowing status via `BorrowingService.book_return`.
    - Dynamic serializer selection based on user role and action.
    - Permission logic:
        - `list`, `create`, `borrowing_return`: Requires authentication.
        - Other actions: Admin-only or read-only for authenticated users.
    """

    queryset = Borrowing.objects.all()
    filterset_class = BorrowingAdminFilter

    def create(self, request, *args, **kwargs):
        serializer = BorrowingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        borrowing = BorrowingService.create_borrowing(
            user=request.user,
            book=serializer.validated_data["book"],
            expected_return=serializer.validated_data["expected_return"],
        )

        response_serializer = self.get_serializer(borrowing)

        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="return")
    def borrowing_return(self, request, pk=None):
        borrowing = self.get_object()
        borrowing = BorrowingService.book_return(borrowing)
        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
