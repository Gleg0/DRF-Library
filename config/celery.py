import os

import django
from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", config("DJANGO_SETTINGS_MODULE")
)
django.setup()

app = Celery("celery_app")

app.config_from_object(config("DJANGO_SETTINGS_MODULE"), namespace="CELERY")

app.conf.enable_utc = True

app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Registers periodic Celery tasks.

    - notify_daily: runs every weekday at 10:00 (Mon–Fri), sends notifications about overdue borrowings.
    - remove_outdated_blacklisted_jwt_from_database: runs daily at midnight (00:00),
      cleans up expired JWT tokens from the database.
    """
    from notifications.tasks import notify_daily

    sender.add_periodic_task(
        crontab(hour=10, minute=0, day_of_week="mon-fri"),
        notify_daily.s(),
    )

    from users.tasks import remove_outdated_blacklisted_jwt_from_database
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        remove_outdated_blacklisted_jwt_from_database.s(),
    )
