from .celery import app as celery_app

__all__ = ['celery_app']

# Optional: specify config directly in Python for window only
celery_app.conf.update(
    worker_pool='solo',
)