from django.core.management.base import BaseCommand

from notifications.services.bot.bot_runner import run


class Command(BaseCommand):
    help = "Run Telegram bot"

    def handle(self, *args, **options):
        run()
