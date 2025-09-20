from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "borrowing",
        "money_to_pay",
        "status",
        "type",
        "session_url",
        "session_id",
    )
