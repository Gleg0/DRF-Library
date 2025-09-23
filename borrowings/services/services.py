from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from base.services.payments_service import StripePaymentService
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class BorrowingService:
    @staticmethod
    def book_return(borrowing):
        if borrowing.actual_return_date:
            raise ValidationError("This book is already returned!")

        with transaction.atomic():
            borrowing.actual_return_date = timezone.now().date()
            borrowing.save(update_fields=["actual_return_date"])
            Book.objects.filter(id=borrowing.book_id).update(
                inventory=F("inventory") + 1
            )

            today = timezone.now().date()
            if (
                borrowing.actual_return_date
                and borrowing.expected_return < today
            ):
                fine_day = (
                    (
                        borrowing.actual_return_date
                        - borrowing.expected_return
                    ).days
                    * borrowing.book.daily_fee
                    * 2
                )
                data = {
                    "product_data": {"name": f"Borrowing #{borrowing.id}"},
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
                "product_data": {"name": f"Borrowing #{borrowing.id}"},
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
