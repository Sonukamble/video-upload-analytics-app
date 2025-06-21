from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from rest_framework import status
from django.db.models import Sum, Count

from django.utils import timezone

from engagement.models import Like


from .models import VideoMetadata, VideoAnalytics
from .serializers import AdminAnalyticsOverviewSerializer, EngagementSerializer, TrackViewSerializer, VideoAnalyticsSummarySerializer

class TrackViewAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        try:
            serializer = TrackViewSerializer(data=request.data)
            if serializer.is_valid():
                video_id = serializer.validated_data['video_id']
                duration = serializer.validated_data['duration']
                user = request.user if request.user.is_authenticated else None

                try:
                    video = VideoMetadata.objects.get(id=video_id)
                except VideoMetadata.DoesNotExist:
                    return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

                analytics, created = VideoAnalytics.objects.get_or_create(video=video)
                analytics.views += 1

                analytics.watch_time.append({
                    "user_id": user.id if user else None,
                    "duration": duration,
                    "timestamp": str(timezone.now())
                })

                analytics.save()

                return Response({"message": "View recorded successfully."}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngagementTrackAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        try:
            serializer = EngagementSerializer(data=request.data)
            if serializer.is_valid():
                video_id = serializer.validated_data['video_id']
                event_type = serializer.validated_data['event_type']
                timestamp = serializer.validated_data['timestamp']
                details = serializer.validated_data.get('details', {})

                try:
                    video = VideoMetadata.objects.get(id=video_id)
                except VideoMetadata.DoesNotExist:
                    return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

                analytics, _ = VideoAnalytics.objects.get_or_create(video=video)

                engagement_entry = {
                    "event_type": event_type,
                    "timestamp": str(timestamp),
                    "details": details,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }

                analytics.engagements.append(engagement_entry)
                analytics.save()

                return Response({"message": "Engagement tracked successfully."}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class VideoAnalyticsSummaryAPIView(APIView):
    def get(self, request, video_id):
        try:
            video = VideoMetadata.objects.get(id=video_id)
        except VideoMetadata.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        analytics, _ = VideoAnalytics.objects.get_or_create(video=video)

        # Calculate average watch time
        watch_times = [entry.get('duration', 0) for entry in analytics.watch_time]
        avg_watch_time = sum(watch_times) / len(watch_times) if watch_times else 0

        # Calculate likes and dislikes from Likes table
        likes_count = Like.objects.filter(video_id=video_id, like_status='like').count()
        dislikes_count = Like.objects.filter(video_id=video_id, like_status='dislike').count()

        response_data = {
            "video_id": video.id,
            "views": analytics.views,
            "likes": likes_count,
            "dislikes": dislikes_count,
            "average_watch_time": avg_watch_time
        }

        # use serializer
        serializer=VideoAnalyticsSummarySerializer(data=response_data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserVideoAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            # Get all videos created by this user
            videos = VideoMetadata.objects.filter(user=user)
            if not videos.exists():
                return Response({"message": "No videos found for this user."}, status=status.HTTP_404_NOT_FOUND)

            analytics_data = []
            for video in videos:
                try:
                    analytics = VideoAnalytics.objects.get(video=video)
                    serializer = VideoAnalyticsSummarySerializer(analytics)
                    data = serializer.data
                    data['video_id'] = str(video.id)
                    data['video_title'] = video.title
                    analytics_data.append(data)
                except VideoAnalytics.DoesNotExist:
                    continue  # Skip if no analytics found

            return Response(analytics_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AdminAnalyticsOverviewAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            total_views = VideoAnalytics.objects.aggregate(total=Sum('views'))['total'] or 0
            total_watch_time = 0
            all_analytics = VideoAnalytics.objects.all()
            for analytics in all_analytics:
                for entry in analytics.watch_time:
                    total_watch_time += entry.get("duration", 0)

            total_likes = Like.objects.filter(like_status='like').count()
            total_dislikes = Like.objects.filter(like_status='dislike').count()

            trending_videos = (
                VideoAnalytics.objects
                .annotate(total=Sum('views'))
                .order_by('-views')[:5]
            )

            trending_data = []
            for item in trending_videos:
                trending_data.append({
                    "video_id": str(item.video.id),
                    "title": item.video.title,
                    "views": item.views
                })

            data = {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_dislikes": total_dislikes,
                "total_watch_time": total_watch_time,
                "trending_videos": trending_data
            }

            serializer = AdminAnalyticsOverviewSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)