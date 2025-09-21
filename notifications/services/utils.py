from datetime import date

from borrowings.models import Borrowing


def borrowings_with_overdue() -> str:
    today = date.today()
    info = Borrowing.objects.filter(
        expected_return__lt=today, actual_return_date__isnull=True
    )
    if info.exists():
        list_response = "\n".join(
            [f"{r.id}, must return {r.expected_return}" for r in info]
        )
    else:
        list_response = "Not found"

    return list_response
