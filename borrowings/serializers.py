from rest_framework import serializers

from books.serializers import BookListSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("id", "actual_return_date")


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.CharField(read_only=True, source="book.title")

    class Meta(BorrowingSerializer.Meta):
        fields = ("id", "borrow_date", "expected_return", "book")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookListSerializer(read_only=True)
