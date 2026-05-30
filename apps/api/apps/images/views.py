"""
Views for image upload and management.
"""
import logging
from datetime import timedelta

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserImage
from .serializers import (
    CompleteUploadSerializer,
    PrepareUploadSerializer,
    UserImageSerializer,
)
from .storage import StorageService, generate_user_image_path
from .tasks import process_user_image

logger = logging.getLogger(__name__)


class UserImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user image management.

    list:     GET /api/user-images/
    retrieve: GET /api/user-images/{id}/
    destroy:  DELETE /api/user-images/{id}/
    """

    serializer_class = UserImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return images owned by current user."""
        return UserImage.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="prepare-upload")
    def prepare_upload(self, request):
        """
        Prepare an image upload by generating a signed upload URL.

        POST /api/user-images/prepare-upload/
        {
            "filename": "photo.jpg",
            "consent_given": true
        }

        Returns:
        {
            "image_id": 123,
            "upload_url": "https://...",
            "upload_fields": {},
            "expires_in": 3600
        }
        """
        serializer = PrepareUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        filename = serializer.validated_data["filename"]
        consent_given = serializer.validated_data["consent_given"]

        try:
            # Generate storage path
            storage_path = generate_user_image_path(
                request.user.id,
                filename,
                prefix="original",
            )

            # Create UserImage record
            user_image = UserImage.objects.create(
                user=request.user,
                original_path=storage_path,
                consent_given=consent_given,
                status=UserImage.ProcessingStatus.PENDING,
            )

            # Generate signed upload URL
            storage = StorageService()
            upload_url = storage.generate_upload_url(
                storage_path,
                expires=timedelta(hours=1),
            )

            logger.info(f"Prepared upload for user {request.user.id}, image {user_image.id}")

            return Response(
                {
                    "image_id": user_image.id,
                    "upload_url": upload_url,
                    "upload_fields": {},  # Can add additional fields if needed
                    "expires_in": 3600,  # 1 hour
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error preparing upload: {e}")
            return Response(
                {"error": "Failed to prepare upload"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_upload(self, request, pk=None):
        """
        Complete an upload and trigger processing.

        POST /api/user-images/{id}/complete/
        {
            "success": true
        }
        """
        user_image = self.get_object()
        serializer = CompleteUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data["success"]:
            user_image.status = UserImage.ProcessingStatus.FAILED
            user_image.error_message = "Upload failed on client side"
            user_image.save()
            return Response(
                {"error": "Upload was not successful"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Verify file exists in storage
            storage = StorageService()
            if not storage.file_exists(user_image.original_path):
                user_image.status = UserImage.ProcessingStatus.FAILED
                user_image.error_message = "File not found in storage"
                user_image.save()
                return Response(
                    {"error": "File not found in storage"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate signed URL for original image
            original_url = storage.generate_download_url(user_image.original_path)
            user_image.original_url = original_url
            user_image.status = UserImage.ProcessingStatus.UPLOADING
            user_image.save()

            # Trigger async processing
            process_user_image.delay(user_image.id)

            logger.info(f"Triggered processing for image {user_image.id}")

            return Response(
                {
                    "message": "Upload completed, processing started",
                    "image": UserImageSerializer(user_image).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error completing upload: {e}")
            user_image.status = UserImage.ProcessingStatus.FAILED
            user_image.error_message = str(e)
            user_image.save()
            return Response(
                {"error": "Failed to complete upload"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """Delete an image and its files from storage."""
        user_image = self.get_object()

        try:
            # Delete files from storage
            storage = StorageService()
            if user_image.original_path:
                storage.delete_file(user_image.original_path)
            if user_image.processed_path:
                storage.delete_file(user_image.processed_path)

            # Delete from database
            user_image.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return Response(
                {"error": "Failed to delete image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
