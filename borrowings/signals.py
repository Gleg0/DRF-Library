from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowings.models import Borrowing
from notifications.tasks import notify_borrowings, notify_payment
from payments.models import Payment


@receiver(post_save, sender=Borrowing)
def create_payment(sender, instance, created, **kwargs):
    if created:
        notify_borrowings.delay(
            borrowing_id=instance.id,
            user_name=instance.user.email,
            book_title=instance.book.title,
            expected_return=instance.expected_return,
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
