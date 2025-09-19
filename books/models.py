from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=5, choices=Cover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=(MinValueValidator(0.01),),
    )

    def __str__(self):
        return (
            f"{self.title} - price per day {self.daily_fee}$."
            f" {self.inventory} is available"
        )
