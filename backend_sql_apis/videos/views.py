from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
import base64
import os
import uuid

from .serializers import VideoMetadataSerializer
from .models import VideoMetadata


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class VideoMetadataCreate(GenericAPIView):
    """
    Create new video metadata for the logged-in user.
    """
    serializer_class = VideoMetadataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Assign the logged-in user to the video metadata.
        Create video metadata and save video/thumbnail files."""
        try:
            serializer = VideoMetadataSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)


        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoMetadataDetail(APIView):
    """
    Retrieve, update or delete a video metadata instance.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_object(self, pk, request):
        try:
            video = VideoMetadata.objects.get(pk=pk)
            self.check_object_permissions(request, video)
            return video
        except VideoMetadata.DoesNotExist:
            return None

    def get(self, request, pk):
        video = self.get_object(pk, request)
        if video:
            serializer = VideoMetadataSerializer(video)
            return Response(serializer.data)
        return Response({'error': 'VideoMetadata not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        video = self.get_object(pk, request)
        if video:
            serializer = VideoMetadataSerializer(video, data=request.data, partial=True)  # allow partial update
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'VideoMetadata not found'}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        video = self.get_object(pk, request)
        if video:
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'VideoMetadata not found'}, status=status.HTTP_404_NOT_FOUND)
