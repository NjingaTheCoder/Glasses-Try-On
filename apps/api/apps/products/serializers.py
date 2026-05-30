"""
Serializers for product management.
"""
from rest_framework import serializers

from .models import Product, ProductImage, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "original_url",
            "cached_path",
            "width",
            "height",
            "position",
            "is_primary",
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants."""

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "title",
            "sku",
            "price",
            "compare_at_price",
            "image_url",
            "option1",
            "option2",
            "option3",
            "inventory_quantity",
            "is_available",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view."""

    store_name = serializers.CharField(source="store.name", read_only=True)
    tag_list = serializers.ListField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "handle",
            "product_url",
            "image_url",
            "price",
            "vendor",
            "tags",
            "tag_list",
            "store",
            "store_name",
            "is_active",
            "created_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view."""

    store_name = serializers.CharField(source="store.name", read_only=True)
    tag_list = serializers.ListField(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "handle",
            "product_url",
            "image_url",
            "price",
            "vendor",
            "tags",
            "tag_list",
            "external_id",
            "store",
            "store_name",
            "variants",
            "images",
            "is_active",
            "created_at",
            "updated_at",
        ]
