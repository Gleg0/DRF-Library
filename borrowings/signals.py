from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from base.services.payments_service import StripePaymentService
from borrowings.models import Borrowing
from notifications.tasks import notify_borrowings, notify_payment
from payments.models import Payment


@receiver(post_save, sender=Borrowing)
def create_payment(sender, instance, created, **kwargs):
    if created:
        rent_day = (instance.expected_return - instance.borrow_date).days
        book_price = instance.book.daily_fee
        total_count = rent_day * book_price
        data = {
            "product_data": {"name": f"Borrowing #{instance.id}"},
            "unit_amount": total_count,
        }
        payment_service = StripePaymentService()
        session = payment_service.create_payment_session(data)

        Payment.objects.create(
            borrowing=instance,
            money_to_pay=total_count,
            session_url=session.url,
            session_id=session.id,
        )
        notify_borrowings.delay(
            borrowing_id=instance.id,
            user_name=instance.user.email,
            book_title=instance.book.title,
            expected_return=instance.expected_return,
        )
    if not created:
        today = timezone.now().date()
        if instance.actual_return_date and instance.expected_return < today:
            fine_day = (
                (instance.actual_return_date - instance.expected_return).days
                * instance.book.daily_fee
                * 2
            )
            data = {
                "product_data": {"name": f"Borrowing #{instance.id}"},
                "unit_amount": fine_day,
            }
            payment_service = StripePaymentService()
            session = payment_service.create_payment_session(data)

            Payment.objects.create(
                borrowing=instance,
                type=Payment.Type.FINE,
                money_to_pay=fine_day,
                session_url=session.url,
                session_id=session.id,
            )


@receiver(post_save, sender=Payment)
def payment_successes(sender, instance, created, **kwargs):
    if not created:
        if instance.status == Payment.Status.PAID:
            notify_payment.delay(
                payment_id=instance.id,
                payment_type=instance.type,
                money_to_pay=instance.money_to_pay,
            )
