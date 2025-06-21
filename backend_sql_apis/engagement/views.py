import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from django.db.models import F, Case, When, IntegerField, Value

from users.models import Profile
from .models import Like, VideoMetadata, Comment, Subscription
from .serializers import LikeCountSerializer, LikeSerializer, CommentSerializer, SubscribedChannelSerializer, SubscriberUserSerializer, SubscriptionSerializer, UserLikeSerializer
        
User = get_user_model()

class LikeVideoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        is_like = request.data.get('is_like', None)

        if is_like is None:
            return Response({"error": "Missing 'is_like' in request body"}, status=status.HTTP_400_BAD_REQUEST)

        like_status = 'like' if is_like else 'dislike'
        user = request.user

        try:
            video = get_object_or_404(VideoMetadata, id=video_id)
            like, created = Like.objects.update_or_create(
                video=video,
                user=user,
                defaults={'like_status': like_status}
            )
            serializer = LikeSerializer(like)
            return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LikeCountAPIView(APIView):
    def get(self, request, video_id):
        try:
            video = VideoMetadata.objects.get(id=video_id)
        except VideoMetadata.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        like_count = Like.objects.filter(video=video, like_status='like').count()
        dislike_count = Like.objects.filter(video=video, like_status='dislike').count()

        serializer = LikeCountSerializer({
            "video_id": video.id,
            "likes": like_count,
            "dislikes": dislike_count
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLikeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        likes = Like.objects.filter(user=user).select_related('video')
        serializer = UserLikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        channel = get_object_or_404(Profile, id=channel_id)

        # Prevent self-subscription
        if channel.user == request.user:
            return Response({"error": "You cannot subscribe to yourself."}, status=status.HTTP_400_BAD_REQUEST)

         # Prevent duplicate subscription
        if Subscription.objects.filter(subscriber=request.user, channel=channel).exists():
            return Response({"message": "Already subscribed."}, status=status.HTTP_200_OK)
        
        # Create subscription
        serializer = SubscriptionSerializer(data={'channel': channel.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(subscriber=request.user)

        # Increment total_subscribers safely using F expression
        Profile.objects.filter(id=channel.id).update(total_subscribers=F('total_subscribers') + 1)

        return Response({"message": "Subscribed successfully."}, status=status.HTTP_201_CREATED)

class UnsubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, channel_id):
        channel = get_object_or_404(Profile, id=channel_id)

        try:
            subscription = Subscription.objects.get(subscriber=request.user, channel=channel)
            subscription.delete()

            # Decrement total_subscribers only if it's greater than 0
            Profile.objects.filter(id=channel.id).update(
                total_subscribers=Case(
                    When(total_subscribers__gt=0, then=F('total_subscribers') - 1),
                    default=0,
                    output_field=IntegerField()
                )
            )

            return Response({"message": "Unsubscribed successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Subscription.DoesNotExist:
            return Response({"error": "You are not subscribed to this channel."}, status=status.HTTP_400_BAD_REQUEST)
        
class MySubscriptionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribedChannelSerializer

    def get_queryset(self):
        return Profile.objects.filter(subscribers__subscriber=self.request.user)

class ChannelSubscribersView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, channelId):
        try:
            channel = Profile.objects.get(id=channelId)
        except Profile.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

        subscriptions = Subscription.objects.filter(channel=channel)

        if request.query_params.get('only') == 'count':
            return Response({'subscriber_count': subscriptions.count()})

        subscribers = [sub.subscriber for sub in subscriptions]
        serializer = SubscriberUserSerializer(subscribers, many=True)
        return Response(serializer.data)
    
class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    # GET - List all comments filtering by the video id
    def get(self, request, comment_id=None):
        if comment_id:
            try:
                comment = Comment.objects.get(id=comment_id)
                serializer = CommentSerializer(comment)
                return Response(serializer.data)
            except Comment.DoesNotExist:
                return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            video_id = request.query_params.get('video', None)
            if video_id:
                comments = Comment.objects.filter(video_id=video_id)
            else:
                comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
    
class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    # DELETE - Only comment owner can delete
    def delete(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id)

            if comment.user != request.user:
                return Response({"error": "You do not have permission to delete this comment."},
                                status=status.HTTP_403_FORBIDDEN)

            comment.delete()
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting user is the owner of the comment
        if comment.user != request.user:
            return Response({"error": "You do not have permission to update this comment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, comment_id=None):
        if comment_id:
            try:
                comment = Comment.objects.get(id=comment_id)
                serializer = CommentSerializer(comment)
                return Response(serializer.data)
            except Comment.DoesNotExist:
                return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)