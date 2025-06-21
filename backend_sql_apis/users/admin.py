from django.contrib import admin
from django_celery_results.models import TaskResult

from .models import CustomUser,Profile
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Profile)
# admin.site.register(TaskResult) # for redis task