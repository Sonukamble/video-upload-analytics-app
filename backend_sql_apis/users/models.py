from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

from .manager import UserManager
from django.conf import settings

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Removing username's unique constraint, as `email` is the primary identifier.
    username = models.CharField(max_length=50, unique=False, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()  # Linking the custom manager

    def __str__(self):
        return self.email
    
class Profile(models.Model):
    title= models.CharField(max_length=100,blank=True,null=True)
    image = models.URLField(blank=True, null=True)  # Google profile image URL
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    total_subscribers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    