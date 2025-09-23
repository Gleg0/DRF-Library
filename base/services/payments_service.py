from abc import ABC, abstractmethod

import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


class BasePaymentService(ABC):
    """
    Basic payment service with abstract methods
    for future payment services
    """

    @abstractmethod
    def create_payment_session(self, data: dict):
        pass

    @abstractmethod
    def is_paid(self, session_id):
        pass

    @abstractmethod
    def mark_session_as_expired(self, session_id):
        pass


class StripePaymentService(BasePaymentService):
    def create_payment_session(self, data: dict):
        """
        Method for create stripe checkout session
        :param data:
        data contain name, borrowing_id, image and cost
        :return:
        stripe session for borrowing service
        """
        success_url = (
            f"{settings.HOST_DOMAIN}{reverse('payments:payment-success')}"
            f"?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = (
            f"{settings.HOST_DOMAIN}{reverse('payments:payment-cancel')}"
            f"?session_id={{CHECKOUT_SESSION_ID}}"
        )

        product_data = {
            "name": data.get("book_name", "Book"),
            "description": data.get("borrowing", "Borrowing#"),
        }

        book_image_url = data.get("book_image_url")
        if book_image_url:
            product_data["images"] = [book_image_url]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": product_data,
                        "unit_amount": int(data["unit_amount"] * 100),
                    },
                    "quantity": data.get("quantity", 1),
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session

    def is_paid(self, session_id):
        """
        Checks stripe payment session status
        :param session_id:
        :return:
        True if status == 'paid', False if 'unpaid'
        """
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == "paid"

    def mark_session_as_expired(self, session_id):
        """
        Marks stripe session as expired
        :param session_id:
        :return:
        Stripe session with expire status
        """
        session = stripe.checkout.Session.expire(session_id)
        return session
