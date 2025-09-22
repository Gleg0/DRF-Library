from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ForeignKey

from borrowings.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PAYMENT,
    )
    borrowing = ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.URLField(max_length=1000)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=(MinValueValidator(0),),
        default=0.00,
    )

    def __str__(self):
        return f"Payment {self.id} - {self.type} - {self.status}"
