from enum import Enum

from celery import shared_task
from telegram import Bot
from decouple import config

from notifications.models import TelegramChat


def send_borrowing_created_message(data: str) -> str:
    return "✅ Borrowing created!" + data


class MessageType(Enum):
    BORROWING_CREATED = "borrowing_created"


@shared_task
def send_telegram_message(message_type: str, data:str):
    bot = Bot(token=config("TELEGRAM_TOKEN", default="telegram-token"))

    if message_type == MessageType.BORROWING_CREATED.value:
        text = send_borrowing_created_message(data)
    else:
        text = "ℹ️ Unknown message type"

    for chat in TelegramChat.objects.all():
        bot.send_message(chat_id=chat.chat_id, text=text)
