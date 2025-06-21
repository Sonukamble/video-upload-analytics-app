import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField  # For PostgreSQL; or use models.JSONField in Django 3.1+

from videos.models import VideoMetadata
from users.models import CustomUser, Profile

class Like(models.Model):
    LIKE_STATUS_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    video = models.ForeignKey(VideoMetadata, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_status = models.CharField(max_length=7, choices=LIKE_STATUS_CHOICES, default='dislike')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user')  # A user can only like or dislike a video once

    def __str__(self):
        return f"{self.user.username} - {self.like_status} - {self.video.title}"


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions',help_text='The user who is subscribing to a channel.')
    channel = models.ForeignKey(
        Profile,on_delete=models.CASCADE, related_name='subscribers',help_text='The user whose channel is being subscribed to')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'channel')  # Prevent duplicate subscriptions
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        
    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.channel.user.username}"

    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(VideoMetadata, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    replies = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Comment by User {self.user.id} on Video {self.video.id}"
