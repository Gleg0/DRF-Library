from abc import ABC, abstractmethod

import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


class BasePaymentService(ABC):
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
        success_url = f"{settings.HOST_DOMAIN}{reverse('payments:payment-success')}?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{settings.HOST_DOMAIN}{reverse('payments:payment-cancel')}?session_id={{CHECKOUT_SESSION_ID}}"
        print(success_url)
        print(cancel_url)
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": data.get(
                            "product_data", {"name": "Product"}
                        ),
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
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == "paid"

    def mark_session_as_expired(self, session_id):
        session = stripe.checkout.Session.expire(session_id)
        return session
