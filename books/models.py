from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from config.settings import base


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=5, choices=Cover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=(MinValueValidator(Decimal(0.01)),),
    )
    image = models.ImageField(
        null=True, blank=True, upload_to="books/photo/"
    )

    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
