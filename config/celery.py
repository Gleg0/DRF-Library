import os
from celery import Celery
from decouple import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config("DJANGO_SETTINGS_MODULE"))

app = Celery("celery_app")

app.config_from_object(config("DJANGO_SETTINGS_MODULE"), namespace="CELERY")

app.autodiscover_tasks()
