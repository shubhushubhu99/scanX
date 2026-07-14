import os
from celery import Celery
import config

def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        backend=getattr(config, "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
        broker=getattr(config, "CELERY_BROKER_URL", "redis://localhost:6379/0")
    )
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return celery

celery = make_celery()

