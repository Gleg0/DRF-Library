from datetime import datetime

from celery import shared_task
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


@shared_task
def remove_outdated_blacklisted_jwt_from_database() -> None:
    """
    Periodic Celery task that cleans up expired JWT tokens.

    - Deletes blacklisted tokens with `token__expires_at` older than the current time.
    - Deletes outstanding tokens with `expires_at` older than the current time.
    """
    BlacklistedToken.objects.filter(token__expires_at__lt=datetime.now()).delete()
    OutstandingToken.objects.filter(expires_at__lt=datetime.now()).delete()
