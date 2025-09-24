from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from base.services.payments_service import StripePaymentService
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

FINE_MULTIPLIER = 2


class BorrowingService:
    @staticmethod
    def book_return(user, borrowing):
        """
        Action for return book with transaction, create new payment with FINE
        status if borrowing have overdue and update inventory
        Increments the book's inventory by +1 after return
        """
        if borrowing.actual_return_date:
            raise ValidationError("This book is already returned!")

        if Payment.objects.filter(
            borrowing__user=user,
            status=Payment.Status.PENDING,
            type=Payment.Type.FINE,
        ).exists():
            raise ValidationError(
                "You can't do this action, "
                "because you have pending payments"
            )

        with transaction.atomic():
            today = timezone.now().date()

            if today <= borrowing.expected_return:
                borrowing.actual_return_date = today
                borrowing.save(update_fields=["actual_return_date"])

                Book.objects.filter(id=borrowing.book_id).update(
                    inventory=F("inventory") + 1
                )

            if borrowing.expected_return < today:
                fine_day = (
                    (today - borrowing.expected_return).days
                    * borrowing.book.daily_fee
                    * FINE_MULTIPLIER
                )
                data = {
                    "borrowing": f"Borrowing #{borrowing.id}",
                    "book_name": borrowing.book.title,
                    "book_image_url": borrowing.book.get_image_url(),
                    "unit_amount": fine_day,
                }
                payment_service = StripePaymentService()
                session = payment_service.create_payment_session(data)

                Payment.objects.create(
                    borrowing=borrowing,
                    type=Payment.Type.FINE,
                    money_to_pay=fine_day,
                    session_url=session.url,
                    session_id=session.id,
                )
        return borrowing

    @staticmethod
    def create_borrowing(user, book, expected_return):
        """
        Action with transaction for creating borrowing
        and new payment with status PENDING
        Decrements the book's inventory by -1
        """
        if Payment.objects.filter(
            borrowing__user=user, status=Payment.Status.PENDING
        ).exists():
            raise ValidationError(
                "You can't create new borrowings, "
                "because you have pending payments"
            )

        with transaction.atomic():
            borrowing = Borrowing.objects.create(
                user=user, book=book, expected_return=expected_return
            )
            Book.objects.filter(id=book.id).update(
                inventory=F("inventory") - 1
            )
            rent_day = (borrowing.expected_return - borrowing.borrow_date).days
            book_price = borrowing.book.daily_fee
            total_count = rent_day * book_price
            data = {
                "book_name": borrowing.book.title,
                "borrowing": f"Borrowing #{borrowing.id}",
                "book_image_url": borrowing.book.get_image_url(),
                "unit_amount": total_count,
            }
            payment_service = StripePaymentService()
            session = payment_service.create_payment_session(data)

            Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=total_count,
                session_url=session.url,
                session_id=session.id,
            )

        return borrowing
