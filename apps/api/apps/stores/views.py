"""
Views for store management and integrations.
"""
import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Store
from .serializers import CSVImportSerializer, ShopifySyncSerializer, StoreSerializer
from .services import CSVImportService, ShopifyService

logger = logging.getLogger(__name__)


class StoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stores.

    list:     GET /api/stores/
    create:   POST /api/stores/
    retrieve: GET /api/stores/{id}/
    update:   PUT /api/stores/{id}/
    partial:  PATCH /api/stores/{id}/
    destroy:  DELETE /api/stores/{id}/
    """

    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return stores owned by the current user.
        Merchants can only see their own stores.
        """
        return Store.objects.filter(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="shopify-sync")
    def shopify_sync(self, request, pk=None):
        """
        Sync products from Shopify.

        POST /api/stores/{id}/shopify-sync/
        {
            "shopify_domain": "mystore.myshopify.com",
            "shopify_access_token": "shpat_xxxxx"
        }

        TODO: Replace manual token input with OAuth flow:
        1. Implement OAuth redirect URL
        2. Handle callback and token exchange
        3. Store token securely
        4. Implement webhook verification
        """
        store = self.get_object()
        serializer = ShopifySyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Initialize Shopify service
            service = ShopifyService(
                domain=serializer.validated_data["shopify_domain"],
                access_token=serializer.validated_data["shopify_access_token"],
            )

            # Sync products
            stats = service.sync_products(store)

            return Response(
                {
                    "message": "Shopify sync completed",
                    "stats": stats,
                },
                status=status.HTTP_200_OK,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify sync failed for store {store.id}: {e}")
            return Response(
                {"error": f"Failed to connect to Shopify: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error during Shopify sync: {e}")
            return Response(
                {"error": "An unexpected error occurred during sync"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="csv-import")
    def csv_import(self, request, pk=None):
        """
        Import products from CSV file.

        POST /api/stores/{id}/csv-import/
        Content-Type: multipart/form-data
        {
            "csv_file": <file>
        }

        CSV format:
        title,product_url,image_url,price,tags
        "T-Shirt","https://example.com/tshirt","https://example.com/img.jpg",29.99,"clothing,casual"
        """
        store = self.get_object()
        serializer = CSVImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        csv_file = serializer.validated_data["csv_file"]

        # Validate CSV format
        errors = CSVImportService.validate_csv(csv_file)
        if errors:
            return Response(
                {"errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Import products
            stats = CSVImportService.import_products(store, csv_file)

            return Response(
                {
                    "message": "CSV import completed",
                    "stats": stats,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"CSV import failed for store {store.id}: {e}")
            return Response(
                {"error": f"Failed to import CSV: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# For backwards compatibility with routes in requirements
import requests
