from django.db import models


class TelegramChat(models.Model):
    chat_id = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)


class BorrowingCreateNotification(models.Model):
    pass