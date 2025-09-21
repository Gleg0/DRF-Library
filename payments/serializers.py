from rest_framework import serializers

from payments.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(
        read_only=True,
        source="borrowing.user.email",
    )

    class Meta:
        model = Payment
        fields = ("id", "type", "status", "money_to_pay", "user")


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing_id = serializers.IntegerField(
        read_only=True,
        source="borrowing.id",
    )
    book = serializers.CharField(
        read_only=True,
        source="borrowing.book.title",
    )
    user = serializers.CharField(
        read_only=True,
        source="borrowing.user.email",
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "money_to_pay",
            "borrowing_id",
            "book",
            "user",
            "session_url",
            "session_id",
        )
