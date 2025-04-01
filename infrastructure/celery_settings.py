from celery import Celery
from .config import settings
app = Celery(
    'tasks',
    broker=f'pyamqp://{settings.celery_user}:'
           f'{settings.celery_password}@localhost//',
    backend='rpc://',
    include=['task_manager.tasks']
)
