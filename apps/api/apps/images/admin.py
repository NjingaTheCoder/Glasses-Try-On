"""
Django admin configuration for images app.
"""
from django.contrib import admin

from .models import ImageMask, UserImage


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    """Admin configuration for UserImage model."""

    list_display = [
        "id",
        "user",
        "status",
        "consent_given",
        "file_size",
        "created_at",
    ]
    list_filter = ["status", "consent_given", "created_at"]
    search_fields = ["user__email", "user__username"]
    readonly_fields = [
        "original_path",
        "processed_path",
        "created_at",
        "updated_at",
        "processed_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "User",
            {
                "fields": ("user", "consent_given"),
            },
        ),
        (
            "Original Image",
            {
                "fields": (
                    "original_path",
                    "original_url",
                    "original_width",
                    "original_height",
                ),
            },
        ),
        (
            "Processed Image",
            {
                "fields": (
                    "processed_path",
                    "processed_url",
                    "processed_width",
                    "processed_height",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("file_size", "mime_type"),
            },
        ),
        (
            "Status",
            {
                "fields": ("status", "error_message"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "processed_at"),
            },
        ),
    )


@admin.register(ImageMask)
class ImageMaskAdmin(admin.ModelAdmin):
    """Admin configuration for ImageMask model."""

    list_display = [
        "id",
        "user_image",
        "mask_type",
        "is_auto_generated",
        "created_at",
    ]
    list_filter = ["mask_type", "is_auto_generated", "created_at"]
    search_fields = ["user_image__user__email"]
    readonly_fields = ["created_at"]
