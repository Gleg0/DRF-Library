from drf_spectacular.utils import OpenApiParameter, extend_schema
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="borrowing_return",
                description="Mark a borrowing as returned",
                required=False,
                type=str,
            ),
        ]
    )
    @action(detail=True, methods=["post"], url_path="return")
    def borrowing_return(self, request, pk=None):
        borrowing = self.get_object()
        borrowing = BorrowingService.book_return(self.request.user, borrowing)
        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset.select_related("book")

        if self.action in ("list", "retrieve"):
            if self.request.user.is_staff:
                queryset = queryset.select_related("user")
            else:
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
