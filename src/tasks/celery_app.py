from celery import Celery
from src.config import settings


celery_instance = Celery(
    "worker",
    broker=settings.redis_url,
    include=["src.tasks.tasks"],
)


celery_instance.conf.beat_schedule = {
    "uvedomlenie": {
        "task": "booking_today_checkin",
        "schedule": 5,
    }
}
