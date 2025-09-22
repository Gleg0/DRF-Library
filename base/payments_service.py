from abc import ABC, abstractmethod

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class BasePaymentService(ABC):
    @abstractmethod
    def create_payment_session(self, data: dict):
        pass

    @abstractmethod
    def is_paid(self, session_id):
        pass


class StripePaymentService(BasePaymentService):
    def create_payment_session(self, data: dict):
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
            success_url=f"http://127.0.0.1:8000/api/payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"http://127.0.0.1:8000/api/payments/cancel/?session_id={{CHECKOUT_SESSION_ID}}",
        )
        return session

    def is_paid(self, session_id):
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == "paid"
