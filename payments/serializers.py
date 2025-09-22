from rest_framework import serializers

from payments.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(
        read_only=True,
        source="borrowing.user.email",
    )
    book = serializers.CharField(
        read_only=True,
        source="borrowing.book.title",
    )
    borrowing_id = serializers.IntegerField(
        read_only=True,
        source="borrowing.id",
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing_id",
            "user",
            "book",
            "type",
            "status",
            "money_to_pay",
        )


class PaymentDetailSerializer(PaymentListSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing_id",
            "book",
            "user",
            "type",
            "status",
            "money_to_pay",
            "session_url",
            "session_id",
        )


class PaymentForBorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "session_url", "session_id")


class PaymentForBorrowingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "money_to_pay",
            "session_url",
            "session_id",
        )
