from django.utils import timezone
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


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("expected_return", "book")

    def validate_book(self, value):
        if value.inventory <= 0:
            raise serializers.ValidationError("This book is not available")
        return value

    def validate(self, attrs):
        Borrowing.validate_expected_return_date(
            borrow_date=timezone.now().date(),
            expected_return=attrs["expected_return"],
            error_to_raise=serializers.ValidationError,
        )
        return attrs

    def create(self, validated_data):
        book = validated_data.pop("book")
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(book=book, **validated_data)
        return borrowing
