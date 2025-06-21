from django.urls import path
from .views import VideoMetadataCreate, VideoMetadataDetail

urlpatterns = [
    path('video-metadata/', VideoMetadataCreate.as_view(), name='video-metadata-list-create'),
    path('video-metadata/<int:pk>/', VideoMetadataDetail.as_view(), name='video-metadata-detail'),
]
