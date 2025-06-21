from django.db import models
from django.conf import settings

# Create your models here.

class VideoMetadata(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('unlisted', 'Unlisted'),
    ]

    DURATION_CHOICES = [
        ('short', 'Short (0-4 minutes)'),
        ('medium', 'Medium (4-20 minutes)'),
        ('long', 'Long (20-60 minutes)'),
        ('very_long', 'Very Long (60+ minutes)'),
    ]

    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True,blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default='short',
        help_text="Categorize video based on its length."
    )
    # Added fields for video and thumbnail file paths
    video_file = models.FileField(upload_to='videos/')
    thumbnail_file = models.ImageField(upload_to='thumbnails/')

    def __str__(self):
        return f"{self.title} ({self.visibility}, {self.duration})"
