from celery import shared_task
from notifications.tg_bot import send_message

@shared_task
def notify(user_name: str, book_title: str, expected_return: str) -> None:
    message = (
        f"New Borrowing\n"
        f"{user_name} take {book_title}\n"
        f"expected_return {expected_return}"
    )
    send_message(message)
