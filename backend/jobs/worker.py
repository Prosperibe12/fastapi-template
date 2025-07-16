from celery import Celery

from backend.core.config import settings

app = Celery(__name__)
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# ----------Task-----------
@app.task(name="test_task")
def test_task():
   print("This is a test task running in Celery worker.")