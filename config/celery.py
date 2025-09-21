import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", config("DJANGO_SETTINGS_MODULE")
)

app = Celery("celery_app")

app.config_from_object(config("DJANGO_SETTINGS_MODULE"), namespace="CELERY")

app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from notifications.tasks import notify_daily
    sender.add_periodic_task(
        crontab(hour=10, day_of_week="mon-fri"),
        notify_daily.s(),
    )