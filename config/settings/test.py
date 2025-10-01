from datetime import timedelta

import stripe

from base.services.payments_service import StripePaymentService
from config.settings.base import *  # noqa: F403,F405

DEBUG = config("DEBUG", default=True, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="dev-secret")
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

INSTALLED_APPS += ["django_extensions"]  # noqa: F403,F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

del REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
}

MESSAGE_TELEGRAM_BOT_TOKEN = "8270003825:AAGkve-gD7ldWKiKTul0Ol74Jnp5Hu3wJcM"

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")

stripe.api_key = STRIPE_SECRET_KEY
PAYMENT_SERVICE = StripePaymentService()
