import os
from celery.schedules import crontab
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('currency_celery_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
