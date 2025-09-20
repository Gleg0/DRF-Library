from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer
