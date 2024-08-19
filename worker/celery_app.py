from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "github_sentinel",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["worker.tasks"]
)

celery_app.conf.beat_schedule = {
    "daily-update": {
        "task": "worker.tasks.daily_update",
        "schedule": 86400.0,  # 24 hours
    },
    "weekly-report": {
        "task": "worker.tasks.weekly_report",
        "schedule": 604800.0,  # 7 days
    },
}
