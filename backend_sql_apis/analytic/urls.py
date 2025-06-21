from django.urls import path
from .views import AdminAnalyticsOverviewAPIView, EngagementTrackAPIView, TrackViewAPIView, UserVideoAnalyticsAPIView, VideoAnalyticsSummaryAPIView

urlpatterns = [
    path('track/view/', TrackViewAPIView.as_view(), name='track-view'),
    path('track/engagement/', EngagementTrackAPIView.as_view(), name='track-engagement'),

    path('get/analytics/<int:video_id>/', VideoAnalyticsSummaryAPIView.as_view(), name='video-analytics-summary'),

    path('get/analytics/user/', UserVideoAnalyticsAPIView.as_view()),

    path('get/analytics/admin/overview/', AdminAnalyticsOverviewAPIView.as_view(), name='admin-analytics-overview'),
    
]