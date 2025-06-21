from django.db import models

from videos.models import VideoMetadata

# Create your models here.
class VideoAnalytics(models.Model):
    video = models.OneToOneField(VideoMetadata, on_delete=models.CASCADE, related_name="analytics")
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    watch_time = models.JSONField(default=list, blank=True)  # [{ "user_id": 1, "duration": 120 }, ...]
    engagements = models.JSONField(default=list, blank=True)  # New field

    def __str__(self):
        return f"Analytics for {self.video.title}"
