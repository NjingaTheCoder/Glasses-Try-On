"""
Serializers for try-on generation.
"""
from rest_framework import serializers

from .models import Generation, GenerationFeedback, TryOnSession


class TryOnSessionSerializer(serializers.ModelSerializer):
    """Serializer for TryOnSession model."""

    generation_count = serializers.IntegerField(
        source="generations.count",
        read_only=True,
    )

    class Meta:
        model = TryOnSession
        fields = [
            "id",
            "user",
            "user_image",
            "store",
            "generation_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class GenerationSerializer(serializers.ModelSerializer):
    """Serializer for Generation model."""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    product_title = serializers.CharField(source="product.title", read_only=True)
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = Generation
        fields = [
            "id",
            "session",
            "user",
            "user_email",
            "user_image",
            "product",
            "product_title",
            "prompt",
            "mask_type",
            "output_path",
            "output_url",
            "status",
            "error_message",
            "openai_request_id",
            "openai_model",
            "processing_time_seconds",
            "celery_task_id",
            "is_complete",
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "prompt",
            "output_path",
            "output_url",
            "status",
            "error_message",
            "openai_request_id",
            "openai_model",
            "processing_time_seconds",
            "celery_task_id",
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
        ]


class CreateGenerationSerializer(serializers.Serializer):
    """Serializer for creating a new generation."""

    user_image_id = serializers.IntegerField(help_text="ID of the user's photo")
    product_id = serializers.IntegerField(help_text="ID of the product to try on")
    session_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional session ID to group generations",
    )
    mask_type = serializers.ChoiceField(
        choices=["UPPER_BODY", "LOWER_BODY", "FULL_BODY", "DRESS", "OUTERWEAR"],
        default="UPPER_BODY",
        help_text="Type of garment/mask to use",
    )


class GenerationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for generation feedback."""

    class Meta:
        model = GenerationFeedback
        fields = [
            "id",
            "generation",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
