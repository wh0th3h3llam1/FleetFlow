import os
import celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

celery_app = celery.Celery("api")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
