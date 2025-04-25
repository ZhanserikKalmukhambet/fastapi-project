from celery import Celery
from app.core.config import get_settings

settings = get_settings()

app = Celery(
    "webhook_worker",
    broker=settings.CELERY_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True
)

app.autodiscover_tasks(["app.tasks.webhook_tasks"])