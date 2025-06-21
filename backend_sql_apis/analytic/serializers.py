from analytic.models import VideoAnalytics
from rest_framework import serializers

class TrackViewSerializer(serializers.Serializer):
    video_id = serializers.CharField()
    duration = serializers.IntegerField(min_value=0)

class EngagementSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    event_type = serializers.ChoiceField(choices=["pause", "resume", "seek", "hover"])
    timestamp = serializers.DateTimeField()
    details = serializers.DictField(required=False)  # Optional extra data


class VideoAnalyticsSummarySerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    views = serializers.IntegerField()
    likes = serializers.IntegerField()
    dislikes = serializers.IntegerField()
    average_watch_time = serializers.FloatField()


class UserVideoAnalyticsSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    title = serializers.CharField()
    views = serializers.IntegerField()
    likes = serializers.IntegerField()
    dislikes = serializers.IntegerField()
    average_watch_time = serializers.FloatField()


class VideoAnalyticsSummarySerializer(serializers.ModelSerializer):
    avg_watch_time = serializers.SerializerMethodField()

    class Meta:
        model = VideoAnalytics
        fields = ['views', 'likes', 'dislikes', 'avg_watch_time']

    def get_avg_watch_time(self, obj):
        durations = [entry['duration'] for entry in obj.watch_time if 'duration' in entry]
        if durations:
            return sum(durations) / len(durations)
        return 0


class AdminAnalyticsOverviewSerializer(serializers.Serializer):
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_dislikes = serializers.IntegerField()
    total_watch_time = serializers.FloatField()
    trending_videos = serializers.ListField(child=serializers.DictField())
