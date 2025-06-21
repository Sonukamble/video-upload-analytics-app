# sql_apis/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sql_apis.settings")  # Replace with your actual project name


app = Celery("sql_apis")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
