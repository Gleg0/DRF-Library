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

    @abstractmethod
    def mark_session_as_expired(self, session_id):
        pass
