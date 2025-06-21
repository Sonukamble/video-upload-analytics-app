from rest_framework import serializers
from .models import VideoMetadata

class VideoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMetadata
        fields = ['id', 'user', 'title', 'description','duration', 'visibility', 'created_at', 'video_file','thumbnail_file']
        read_only_fields = ['user', 'created_at']  # Prevent user from being modified directly
