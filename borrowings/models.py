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
