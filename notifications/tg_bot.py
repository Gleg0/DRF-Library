import telebot
from decouple import config

TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(config("TELEGRAM_CHAT_ID"))


bot = telebot.TeleBot(TELEGRAM_TOKEN)


def send_message(text: str) -> None:
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        print("✅")
    except Exception as e:
        print("❌")
