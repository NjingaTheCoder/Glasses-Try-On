"""
Django admin configuration for tryon app.
"""
from django.contrib import admin

from .models import Generation, GenerationFeedback, TryOnSession


@admin.register(TryOnSession)
class TryOnSessionAdmin(admin.ModelAdmin):
    """Admin configuration for TryOnSession model."""

    list_display = ["id", "user", "user_image", "store", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    """Admin configuration for Generation model."""

    list_display = [
        "id",
        "user",
        "product",
        "status",
        "processing_time_seconds",
        "created_at",
    ]
    list_filter = ["status", "mask_type", "created_at"]
    search_fields = [
        "user__email",
        "product__title",
        "celery_task_id",
        "openai_request_id",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
        "celery_task_id",
        "openai_request_id",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("session", "user", "user_image", "product"),
            },
        ),
        (
            "Generation Settings",
            {
                "fields": ("prompt", "mask_type"),
            },
        ),
        (
            "Output",
            {
                "fields": ("output_path", "output_url"),
            },
        ),
        (
            "Status",
            {
                "fields": ("status", "error_message"),
            },
        ),
        (
            "OpenAI Metadata",
            {
                "fields": (
                    "openai_request_id",
                    "openai_model",
                    "processing_time_seconds",
                ),
            },
        ),
        (
            "Task Tracking",
            {
                "fields": ("celery_task_id",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "started_at",
                    "completed_at",
                ),
            },
        ),
    )


@admin.register(GenerationFeedback)
class GenerationFeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for GenerationFeedback model."""

    list_display = ["id", "generation", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["generation__id", "comment"]
    readonly_fields = ["created_at"]
