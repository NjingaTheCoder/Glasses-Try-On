"""
Views for product browsing.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .serializers import ProductDetailSerializer, ProductListSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing products.

    list:     GET /api/products/?store_id=1
    retrieve: GET /api/products/{id}/

    Products are read-only through the API.
    They are created/updated via store sync/import.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        """
        Return products filtered by store.

        Query parameters:
        - store_id: Filter by store ID (required for customers, optional for merchants)
        - search: Search in title, tags, vendor
        """
        queryset = Product.objects.filter(is_active=True).select_related("store")

        # Filter by store
        store_id = self.request.query_params.get("store_id")
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        # Only allow users to see products from stores they own or public stores
        user = self.request.user
        if not user.is_merchant:
            # Customers can see all active products
            pass
        else:
            # Merchants can only see their own products
            if not store_id:
                queryset = queryset.filter(store__owner=user)

        # Search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(tags__icontains=search)

        return queryset.prefetch_related("variants", "images")
