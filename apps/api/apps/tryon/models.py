"""
Try-on generation models.
"""
from django.conf import settings
from django.db import models

from apps.images.models import UserImage
from apps.products.models import Product


class TryOnSession(models.Model):
    """
    Try-on session grouping multiple generations.

    A session represents a user's browsing session where they try on multiple items.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tryon_sessions",
    )
    user_image = models.ForeignKey(
        UserImage,
        on_delete=models.CASCADE,
        related_name="tryon_sessions",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="tryon_sessions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tryon_sessions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session {self.id} by {self.user.email}"


class Generation(models.Model):
    """
    Individual try-on generation record.

    Tracks the entire lifecycle of a try-on generation from creation to completion.
    """

    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        PROCESSING = "PROCESSING", "Processing"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"

    session = models.ForeignKey(
        TryOnSession,
        on_delete=models.CASCADE,
        related_name="generations",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generations",
    )
    user_image = models.ForeignKey(
        UserImage,
        on_delete=models.CASCADE,
        related_name="generations",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="generations",
    )

    # Generation settings
    prompt = models.TextField(
        help_text="Full prompt sent to OpenAI",
    )
    mask_type = models.CharField(
        max_length=20,
        default="UPPER_BODY",
        help_text="Type of mask used (if any)",
    )

    # Output
    output_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to generated image in S3/MinIO",
    )
    output_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Signed URL for generated image",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    error_message = models.TextField(blank=True)

    # OpenAI metadata
    openai_request_id = models.CharField(max_length=255, blank=True)
    openai_model = models.CharField(max_length=100, blank=True)
    processing_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to generate (seconds)",
    )

    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "generations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["session", "status"]),
            models.Index(fields=["celery_task_id"]),
        ]

    def __str__(self):
        return f"Generation {self.id} - {self.status}"

    @property
    def is_complete(self):
        """Check if generation is in a final state."""
        return self.status in [self.Status.SUCCEEDED, self.Status.FAILED]


class GenerationFeedback(models.Model):
    """
    User feedback on generations.

    Allows users to rate and provide feedback on try-on results.
    """

    class Rating(models.IntegerChoices):
        POOR = 1, "Poor"
        FAIR = 2, "Fair"
        GOOD = 3, "Good"
        EXCELLENT = 4, "Excellent"

    generation = models.OneToOneField(
        Generation,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    rating = models.IntegerField(choices=Rating.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "generation_feedback"

    def __str__(self):
        return f"Feedback for Generation {self.generation.id}: {self.get_rating_display()}"
