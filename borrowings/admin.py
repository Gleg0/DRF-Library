from django.contrib import admin

from borrowings.models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "borrow_date", "expected_return", "actual_return_date",)
