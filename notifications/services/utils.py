from datetime import date

from borrowings.models import Borrowing


def borrowings_with_overdue() -> str:
    today = date.today()
    info = Borrowing.objects.filter(
        expected_return__lt=today, actual_return_date__isnull=True
    )
    if info.exists():
        list_response = "📢 Outdate borrowings:\n\n" + "\n\n".join(
            [
                (
                    f"📌 Borrowing ID: {r.id}\n"
                    f"👤 User: {r.user.email}\n"
                    f"📖 Book: {r.book.title}\n"
                    f"📅 Expected return: {r.expected_return}"
                )
                for r in info
            ]
        )
    else:
        list_response = "📢 Check completed 📢\n" "No records found"

    return list_response


def new_borrowing(
    borrowing_id: str, user_name: str, book_title: str, expected_return: str
):
    return (
        f"✨ New Borrowing №{borrowing_id}\n\n"
        f"👤 User: {user_name}\n"
        f"📖 Book: {book_title}\n"
        f"📅 Expected return: {expected_return}"
    )


def payment_success(payment_id: int, payment_type: str, money_to_pay: float):
    return (
        f"💳 Payment №{payment_id}\n\n"
        f"📌 Type: {payment_type}\n"
        f"💰 Amount: {money_to_pay}"
    )
