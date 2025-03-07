# video_conf/celery.py
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_conf.settings')

# Create Celery app
app = Celery('video_conf')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()