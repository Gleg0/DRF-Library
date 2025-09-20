from django.db import models

from books.models import Book
from config.settings import base


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        base.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    @staticmethod
    def validate_expected_return_date(
        borrow_date, expected_return, error_to_raise
    ):
        if expected_return <= borrow_date:
            raise error_to_raise(
                {
                    "expected_date": "Expected return date "
                    "must be after the borrow date"
                }
            )

    def __str__(self):
        return f"{self.user} take {self.book}"
