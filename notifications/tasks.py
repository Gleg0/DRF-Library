from celery import shared_task

from notifications.services import utils
from notifications.tg_bot import send_message


@shared_task
def notify_daily() -> None:
    send_message(utils.borrowings_with_overdue())


@shared_task
def notify_borrowings(user_name: str, book_title: str, expected_return: str) -> None:
    message = (
        f"New Borrowing\n"
        f"{user_name} took {book_title}\n"
        f"Expected return: {expected_return}"
    )
    send_message(message)
