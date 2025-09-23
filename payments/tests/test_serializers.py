import unittest
from payments.serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentForBorrowingCreateSerializer,
    PaymentForBorrowingDetailSerializer,
)
from payments.models import Payment


class DummyUser:
    def __init__(self, email):
        self.email = email


class DummyBook:
    def __init__(self, title):
        self.title = title


class DummyBorrowing:
    def __init__(self, id, user, book):
        self.id = id
        self.user = user
        self.book = book


class DummyPayment:
    def __init__(
        self,
        id,
        type,
        status,
        money_to_pay,
        borrowing=None,
        session_url=None,
        session_id=None,
    ):
        self.id = id
        self.type = type
        self.status = status
        self.money_to_pay = money_to_pay
        self.borrowing = borrowing
        self.session_url = session_url
        self.session_id = session_id


class PaymentSerializerTestCase(unittest.TestCase):
    def test_payment_list_serializer_fields(self):
        serializer = PaymentListSerializer()
        self.assertEqual(
            set(serializer.fields.keys()),
            {
                "id",
                "borrowing_id",
                "user",
                "book",
                "type",
                "status",
                "money_to_pay",
            },
        )

    def test_payment_detail_serializer_fields(self):
        serializer = PaymentDetailSerializer()
        self.assertEqual(
            set(serializer.fields.keys()),
            {
                "id",
                "borrowing_id",
                "book",
                "user",
                "type",
                "status",
                "money_to_pay",
                "session_url",
                "session_id",
            },
        )

    def test_payment_for_borrowing_create_fields(self):
        serializer = PaymentForBorrowingCreateSerializer()
        self.assertEqual(
            set(serializer.fields.keys()), {"id", "session_url", "session_id"}
        )

    def test_payment_for_borrowing_detail_fields(self):
        serializer = PaymentForBorrowingDetailSerializer()
        self.assertEqual(
            set(serializer.fields.keys()),
            {
                "id",
                "type",
                "status",
                "money_to_pay",
                "session_url",
                "session_id",
            },
        )

    def test_payment_list_serializer_output(self):
        borrowing = DummyBorrowing(
            id=10,
            user=DummyUser(email="test@example.com"),
            book=DummyBook(title="Clean Code"),
        )
        payment = DummyPayment(
            id=1,
            type=Payment.Type.PAYMENT,
            status=Payment.Status.PENDING,
            money_to_pay="50.00",
            borrowing=borrowing,
        )
        serializer = PaymentListSerializer(payment)
        data = serializer.data

        self.assertEqual(data["id"], 1)
        self.assertEqual(data["borrowing_id"], 10)
        self.assertEqual(data["user"], "test@example.com")
        self.assertEqual(data["book"], "Clean Code")
        self.assertEqual(data["type"], Payment.Type.PAYMENT)
        self.assertEqual(data["status"], Payment.Status.PENDING)
        self.assertEqual(data["money_to_pay"], "50.00")

    def test_payment_detail_serializer_output(self):
        borrowing = DummyBorrowing(
            id=42,
            user=DummyUser(email="lev@example.com"),
            book=DummyBook(title="Python Tricks"),
        )
        payment = DummyPayment(
            id=5,
            type=Payment.Type.FINE,
            status=Payment.Status.PAID,
            money_to_pay="10.50",
            borrowing=borrowing,
            session_url="http://test.com/session",
            session_id="abc123",
        )
        serializer = PaymentDetailSerializer(payment)
        data = serializer.data

        self.assertEqual(data["id"], 5)
        self.assertEqual(data["borrowing_id"], 42)
        self.assertEqual(data["user"], "lev@example.com")
        self.assertEqual(data["book"], "Python Tricks")
        self.assertEqual(data["type"], Payment.Type.FINE)
        self.assertEqual(data["status"], Payment.Status.PAID)
        self.assertEqual(data["money_to_pay"], "10.50")
        self.assertEqual(data["session_url"], "http://test.com/session")
        self.assertEqual(data["session_id"], "abc123")


if __name__ == "__main__":
    unittest.main()
