"""Setup celery configuration for application with the broker and result backend."""
from celery import Celery
from loguru import logger

from backend.core.config import settings

app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['backend.jobs.tasks']
)

if __name__ == "__main__":
    logger.info("Starting Celery worker...")
    app.start()
