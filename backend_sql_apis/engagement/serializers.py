from rest_framework import serializers
from django.contrib.auth import get_user_model

from videos.models import VideoMetadata
from .models import Like, Subscription, Comment
from users.models import Profile

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'video', 'like_status', 'created_at']

    def create(self, validated_data):
        """Automatically assign the logged-in user"""
        validated_data['user']= self.context['request'].user
        return super().create(validated_data)

class LikeCountSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()
    likes = serializers.IntegerField()
    dislikes = serializers.IntegerField()

class VideoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMetadata
        fields = ['id', 'title', 'description']  # add more fields if needed

class UserLikeSerializer(serializers.ModelSerializer):
    video = VideoMetadataSerializer()

    class Meta:
        model = Like
        fields = ['video', 'like_status', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['subscriber', 'channel', 'created_at']
        read_only_fields = ['subscriber', 'created_at']

    def validate_channel(self, channel):
        subscriber = self.context['request'].user
        if Subscription.objects.filter(subscriber=subscriber, channel=channel).exists():
            raise serializers.ValidationError("Already subscribed to this channel.")
        return channel

class SubscribedChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'title', 'image', 'description']

User = get_user_model()

class SubscriberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Customize as needed

class ReplySerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    comment_text = serializers.CharField(required=False, allow_blank=True)

class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user', 'comment_text', 'replies']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        replies_data = validated_data.pop('replies', [])
        user = self.context['request'].user  # Get user from context
        comment = Comment.objects.create(user=user, **validated_data)
        comment.replies = replies_data
        comment.save()
        return comment