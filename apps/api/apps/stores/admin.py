"""
Django admin configuration for stores app.
"""
from django.contrib import admin

from .models import Store, StoreAPIKey


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """Admin configuration for Store model."""

    list_display = [
        "name",
        "owner",
        "integration_type",
        "is_active",
        "product_count",
        "created_at",
    ]
    list_filter = ["integration_type", "is_active", "created_at"]
    search_fields = ["name", "owner__email", "shopify_domain"]
    readonly_fields = ["created_at", "updated_at", "last_synced_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("name", "description", "owner", "is_active"),
            },
        ),
        (
            "Integration",
            {
                "fields": (
                    "integration_type",
                    "shopify_domain",
                    "shopify_access_token",
                    "last_synced_at",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(StoreAPIKey)
class StoreAPIKeyAdmin(admin.ModelAdmin):
    """Admin configuration for StoreAPIKey model."""

    list_display = ["key_name", "store", "key_type", "is_active", "created_at"]
    list_filter = ["key_type", "is_active", "created_at"]
    search_fields = ["key_name", "store__name"]
    readonly_fields = ["created_at"]
