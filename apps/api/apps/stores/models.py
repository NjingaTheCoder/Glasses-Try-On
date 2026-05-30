"""
Store models for multi-tenant merchant management.
"""
from django.conf import settings
from django.db import models


class Store(models.Model):
    """
    Store model representing a merchant's store.

    Supports multiple stores per merchant.
    Each store can connect to Shopify or import products via CSV.
    """

    class IntegrationType(models.TextChoices):
        SHOPIFY = "SHOPIFY", "Shopify"
        CSV = "CSV", "CSV Import"
        MANUAL = "MANUAL", "Manual"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stores",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    integration_type = models.CharField(
        max_length=20,
        choices=IntegrationType.choices,
        default=IntegrationType.MANUAL,
    )

    # Shopify integration fields
    shopify_domain = models.CharField(max_length=255, blank=True)
    shopify_access_token = models.CharField(max_length=255, blank=True)
    shopify_webhook_secret = models.CharField(max_length=255, blank=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stores"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.owner.email})"

    @property
    def product_count(self):
        """Get the number of products in this store."""
        return self.products.count()


class StoreAPIKey(models.Model):
    """
    API keys for store integrations (Shopify, etc.).

    Separate model for better security and key rotation.
    """

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    key_name = models.CharField(max_length=100)
    key_value = models.CharField(max_length=500)
    key_type = models.CharField(max_length=50)  # e.g., "shopify_admin_api"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "store_api_keys"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.key_name} for {self.store.name}"
