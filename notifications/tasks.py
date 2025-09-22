from celery import shared_task

from notifications.services import utils
from notifications.tg_bot import send_message


@shared_task
def notify_daily() -> None:
    send_message(utils.borrowings_with_overdue())


@shared_task
def notify_borrowings(*args, **kwargs) -> None:
    send_message(utils.new_borrowing(*args, **kwargs))
