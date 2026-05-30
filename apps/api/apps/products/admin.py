"""
Django admin configuration for products app.
"""
from django.contrib import admin

from .models import Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""

    model = ProductImage
    extra = 0
    fields = ["original_url", "cached_path", "position", "is_primary"]


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""

    model = ProductVariant
    extra = 0
    fields = ["title", "sku", "price", "option1", "option2", "is_available"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""

    list_display = [
        "title",
        "store",
        "price",
        "vendor",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "store", "created_at"]
    search_fields = ["title", "handle", "tags", "vendor"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProductVariantInline, ProductImageInline]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("store", "title", "handle", "product_url"),
            },
        ),
        (
            "Pricing & Details",
            {
                "fields": ("price", "vendor", "tags"),
            },
        ),
        (
            "Media",
            {
                "fields": ("image_url",),
            },
        ),
        (
            "Integration",
            {
                "fields": ("external_id", "is_active"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for ProductVariant model."""

    list_display = [
        "title",
        "product",
        "price",
        "sku",
        "is_available",
    ]
    list_filter = ["is_available", "created_at"]
    search_fields = ["title", "sku", "product__title"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""

    list_display = [
        "product",
        "original_url",
        "is_primary",
        "position",
    ]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["product__title"]
