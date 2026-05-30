"""
Serializers for image management.
"""
from rest_framework import serializers

from .models import ImageMask, UserImage


class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for UserImage model."""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserImage
        fields = [
            "id",
            "user",
            "user_email",
            "original_path",
            "original_url",
            "processed_path",
            "processed_url",
            "original_width",
            "original_height",
            "processed_width",
            "processed_height",
            "file_size",
            "mime_type",
            "consent_given",
            "status",
            "error_message",
            "created_at",
            "updated_at",
            "processed_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "original_url",
            "processed_path",
            "processed_url",
            "original_width",
            "original_height",
            "processed_width",
            "processed_height",
            "file_size",
            "mime_type",
            "status",
            "error_message",
            "created_at",
            "updated_at",
            "processed_at",
        ]


class PrepareUploadSerializer(serializers.Serializer):
    """Serializer for upload preparation request."""

    filename = serializers.CharField(
        max_length=255,
        help_text="Original filename (e.g., photo.jpg)",
    )
    consent_given = serializers.BooleanField(
        default=True,
        help_text="User consent for image processing",
    )

    def validate_filename(self, value):
        """Validate filename has an image extension."""
        allowed_extensions = ["jpg", "jpeg", "png", "webp"]
        extension = value.rsplit(".", 1)[-1].lower() if "." in value else ""
        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File must have one of these extensions: {', '.join(allowed_extensions)}"
            )
        return value


class CompleteUploadSerializer(serializers.Serializer):
    """Serializer for upload completion."""

    success = serializers.BooleanField(
        help_text="Whether the upload was successful",
    )


class ImageMaskSerializer(serializers.ModelSerializer):
    """Serializer for ImageMask model."""

    class Meta:
        model = ImageMask
        fields = [
            "id",
            "user_image",
            "mask_type",
            "mask_path",
            "mask_url",
            "width",
            "height",
            "is_auto_generated",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "mask_url",
            "created_at",
        ]
