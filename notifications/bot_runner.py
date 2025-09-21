from notifications.tg_bot import bot, TELEGRAM_CHAT_ID
from notifications.services import utils


@bot.message_handler(commands=["list"])
def handle_list(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=utils.borrowings_with_overdue())


def run():
    bot.polling(none_stop=True)
