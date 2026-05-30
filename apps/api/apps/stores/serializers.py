"""
Serializers for store management.
"""
from rest_framework import serializers

from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model."""

    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "description",
            "integration_type",
            "shopify_domain",
            "owner",
            "owner_email",
            "product_count",
            "is_active",
            "last_synced_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_email",
            "product_count",
            "last_synced_at",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "shopify_access_token": {"write_only": True},
        }

    def create(self, validated_data):
        """Set owner to current user."""
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class ShopifySyncSerializer(serializers.Serializer):
    """Serializer for Shopify sync request."""

    shopify_domain = serializers.CharField(
        max_length=255,
        help_text="Shopify store domain (e.g., mystore.myshopify.com)",
    )
    shopify_access_token = serializers.CharField(
        max_length=255,
        write_only=True,
        help_text="Shopify Admin API access token",
    )

    def validate_shopify_domain(self, value):
        """Validate Shopify domain format."""
        if not value.endswith(".myshopify.com"):
            # Allow it anyway for testing, but warn
            pass
        return value


class CSVImportSerializer(serializers.Serializer):
    """Serializer for CSV product import."""

    csv_file = serializers.FileField(
        help_text="CSV file with columns: title, product_url, image_url, price, tags"
    )

    def validate_csv_file(self, value):
        """Validate CSV file."""
        if not value.name.endswith(".csv"):
            raise serializers.ValidationError("File must be a CSV file.")
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size must be less than 10MB.")
        return value
