from time import sleep
from src.tasks.celery_app import celery_instance

@celery_instance.task(name="test_task")
def test_task():
    sleep(5)
    print("Test task completed")