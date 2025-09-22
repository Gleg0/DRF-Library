from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from books.models import Book


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
        return borrowing
