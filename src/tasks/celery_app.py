from celery import Celery
from src.config import settings


celery_instance = Celery(
    "worker", 
    broker=settings.redis_url, 
    include=[
        "src.tasks.tasks"
        ],
)