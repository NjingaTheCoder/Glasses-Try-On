"""
Product models for merchandise catalog.
"""
from django.db import models

from apps.stores.models import Store


class Product(models.Model):
    """
    Product model representing clothing items.

    Products belong to a store and can have multiple variants.
    """

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="products",
    )
    title = models.CharField(max_length=500)
    handle = models.CharField(max_length=500, blank=True)
    product_url = models.URLField(max_length=1000)
    image_url = models.URLField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.CharField(max_length=255, blank=True)
    tags = models.TextField(blank=True, help_text="Comma-separated tags")

    # External integration fields
    external_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="External ID from Shopify or other platforms",
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store", "is_active"]),
            models.Index(fields=["external_id"]),
        ]
        unique_together = [["store", "external_id"]]

    def __str__(self):
        return f"{self.title} - {self.store.name}"

    @property
    def tag_list(self):
        """Get tags as a list."""
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class ProductVariant(models.Model):
    """
    Product variant model for different options (size, color, etc.).

    Each variant has its own price and SKU.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    image_url = models.URLField(max_length=1000, blank=True)

    # Variant options
    option1 = models.CharField(max_length=255, blank=True)  # e.g., "Small", "Red"
    option2 = models.CharField(max_length=255, blank=True)
    option3 = models.CharField(max_length=255, blank=True)

    # External ID for sync
    external_id = models.CharField(max_length=255, blank=True)

    # Inventory
    inventory_quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_variants"
        ordering = ["product", "title"]

    def __str__(self):
        return f"{self.product.title} - {self.title}"


class ProductImage(models.Model):
    """
    Product images with caching.

    Stores downloaded copies of product images for faster access.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    original_url = models.URLField(max_length=1000)
    cached_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path in S3/MinIO storage",
    )
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    position = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"
        ordering = ["product", "position"]

    def __str__(self):
        return f"Image for {self.product.title}"
