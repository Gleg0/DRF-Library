from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ForeignKey

from borrowings.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.PENDING,
    )
    type = models.CharField(
        max_length=7,
        choices=Type.choices,
        default=Type.PAYMENT,
    )
    borrowing = ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=(MinValueValidator(0),),
        default=0.00,
    )

    def __str__(self):
        return f"Payment id: {self.id}"
