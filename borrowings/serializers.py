from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from books.serializers import BookListSerializer
from borrowings.models import Borrowing
from users.serializers import UserDetailSerializer, UserListSerializer


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

    class Meta(BorrowingSerializer.Meta):
        read_only_fields = BorrowingSerializer.Meta.read_only_fields + (
            "expected_return",
            "book",
        )


class BorrowingAdminListSerializer(BorrowingListSerializer):
    user = UserListSerializer(read_only=True, many=False)

    class Meta(BorrowingListSerializer.Meta):
        fields = BorrowingListSerializer.Meta.fields + ("user",)


class BorrowingAdminDetailSerializer(BorrowingDetailSerializer):
    user = UserDetailSerializer(read_only=True, many=False)

    class Meta(BorrowingDetailSerializer.Meta):
        fields = BorrowingDetailSerializer.Meta.fields + ("user",)


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(read_only=True, source="book.title")

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return", "book", "book_title")
        extra_kwargs = {"book": {"write_only": True}}

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


class BorrowingReturnSerializer(BorrowingDetailSerializer):
    book = serializers.CharField(read_only=True, source="book.title")
