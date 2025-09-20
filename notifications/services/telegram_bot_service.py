from django.conf import settings

from base.services.telegram_bot_service import BaseTelegramBotService


class TelegramBotService(BaseTelegramBotService):
    def __init__(self, token=settings.MESSAGE_TELEGRAM_BOT_TOKEN):
        super().__init__(token)
