import os

from celery import Celery

celery_broker_url = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
app = Celery(
    'tasks',
    broker=celery_broker_url,
    backend='rpc://',
    include=['app.infrastructure.task_manager.tasks']
)
