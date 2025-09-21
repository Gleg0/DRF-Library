import telebot


class BaseTelegramBotService:
    def __init__(self, token: str):
        self._bot = telebot.TeleBot(token)

    def send_message(self, chat_id: int, text: str, **kwargs):
        self._bot.send_message(chat_id, text, **kwargs)
