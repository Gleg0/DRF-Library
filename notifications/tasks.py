from celery import shared_task

from notifications.services import utils
from notifications.services.bot.tg_bot import send_message


@shared_task
def notify_daily() -> None:
    """
    Periodic Celery task that sends notifications
    about overdue borrowings to admins.
    """
    send_message(utils.borrowings_with_overdue())


@shared_task
def notify_borrowings(*args, **kwargs) -> None:
    """
    Celery task that sends a notification about a newly created borrowing.
    """
    send_message(utils.new_borrowing(*args, **kwargs))


@shared_task
def notify_payment(*args, **kwargs):
    """
    Celery task that sends a notification about a successful payment.
    """
    send_message(utils.payment_success(*args, **kwargs))
