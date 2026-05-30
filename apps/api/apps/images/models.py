"""
Image models for user photo uploads and processing.
"""
from django.conf import settings
from django.db import models


class UserImage(models.Model):
    """
    User-uploaded images for try-on generation.

    Stores original and processed versions with metadata.
    """

    class ProcessingStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Upload"
        UPLOADING = "UPLOADING", "Uploading"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
    )

    # Original image
    original_path = models.CharField(
        max_length=500,
        help_text="Path to original image in S3/MinIO",
    )
    original_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Signed URL for original image",
    )

    # Processed image
    processed_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to processed image in S3/MinIO",
    )
    processed_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Signed URL for processed image",
    )

    # Image metadata
    original_width = models.IntegerField(null=True, blank=True)
    original_height = models.IntegerField(null=True, blank=True)
    processed_width = models.IntegerField(null=True, blank=True)
    processed_height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes",
    )
    mime_type = models.CharField(max_length=100, blank=True)

    # Consent and privacy
    consent_given = models.BooleanField(
        default=False,
        help_text="User consent for image processing",
    )

    # Processing status
    status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_images"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"Image {self.id} by {self.user.email} ({self.status})"


class ImageMask(models.Model):
    """
    Segmentation masks for user images.

    Used to target specific body parts for try-on.
    Optional: Can be auto-generated or manually uploaded.
    """

    class MaskType(models.TextChoices):
        UPPER_BODY = "UPPER_BODY", "Upper Body"
        LOWER_BODY = "LOWER_BODY", "Lower Body"
        FULL_BODY = "FULL_BODY", "Full Body"
        CUSTOM = "CUSTOM", "Custom"

    user_image = models.ForeignKey(
        UserImage,
        on_delete=models.CASCADE,
        related_name="masks",
    )
    mask_type = models.CharField(
        max_length=20,
        choices=MaskType.choices,
        default=MaskType.UPPER_BODY,
    )
    mask_path = models.CharField(
        max_length=500,
        help_text="Path to mask image in S3/MinIO",
    )
    mask_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Signed URL for mask image",
    )

    # Mask metadata
    width = models.IntegerField()
    height = models.IntegerField()

    # Generation method
    is_auto_generated = models.BooleanField(
        default=False,
        help_text="True if generated automatically, False if manually uploaded",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "image_masks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.mask_type} mask for {self.user_image}"
