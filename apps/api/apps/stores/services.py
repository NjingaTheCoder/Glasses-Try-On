"""
Business logic for store integrations.
"""
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List

import requests
from django.db import transaction
from django.utils import timezone

from apps.products.models import Product

logger = logging.getLogger(__name__)


class ShopifyService:
    """
    Service for Shopify integration.

    TODO: Complete OAuth flow implementation:
    1. Redirect user to Shopify OAuth URL
    2. Handle callback with authorization code
    3. Exchange code for access token
    4. Store token securely
    """

    def __init__(self, domain: str, access_token: str):
        self.domain = domain
        self.access_token = access_token
        self.base_url = f"https://{domain}/admin/api/2024-01"

    def get_headers(self) -> Dict[str, str]:
        """Get headers for Shopify API requests."""
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    def sync_products(self, store) -> Dict[str, int]:
        """
        Sync products from Shopify.

        Returns:
            Dict with counts: {"created": 5, "updated": 10, "errors": 0}
        """
        stats = {"created": 0, "updated": 0, "errors": 0}

        try:
            # Fetch products from Shopify
            products_data = self._fetch_all_products()

            # Process each product
            for product_data in products_data:
                try:
                    self._sync_product(store, product_data)
                    stats["created"] += 1
                except Exception as e:
                    logger.error(f"Error syncing product {product_data.get('id')}: {e}")
                    stats["errors"] += 1

            # Update last sync time
            store.last_synced_at = timezone.now()
            store.integration_type = "SHOPIFY"
            store.shopify_domain = self.domain
            store.shopify_access_token = self.access_token
            store.save()

        except Exception as e:
            logger.error(f"Error syncing products from Shopify: {e}")
            raise

        return stats

    def _fetch_all_products(self) -> List[Dict]:
        """
        Fetch all products from Shopify with pagination.

        TODO: Implement proper pagination using cursor-based pagination
        """
        url = f"{self.base_url}/products.json"
        response = requests.get(url, headers=self.get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("products", [])

    @transaction.atomic
    def _sync_product(self, store, product_data: Dict):
        """Sync a single product from Shopify."""
        # Extract product data
        shopify_product_id = str(product_data["id"])
        title = product_data["title"]
        handle = product_data.get("handle", "")
        product_url = f"https://{self.domain}/products/{handle}"
        vendor = product_data.get("vendor", "")
        tags = product_data.get("tags", "")

        # Get first image
        images = product_data.get("images", [])
        image_url = images[0]["src"] if images else ""

        # Get first variant for price
        variants = product_data.get("variants", [])
        price = float(variants[0]["price"]) if variants else 0.0

        # Create or update product
        product, created = Product.objects.update_or_create(
            store=store,
            external_id=shopify_product_id,
            defaults={
                "title": title,
                "handle": handle,
                "product_url": product_url,
                "price": price,
                "vendor": vendor,
                "tags": tags,
                "image_url": image_url,
            },
        )

        return product


class CSVImportService:
    """
    Service for CSV product import.

    Expected CSV columns:
    - title (required)
    - product_url (required)
    - image_url (required)
    - price (required)
    - tags (optional)
    """

    REQUIRED_COLUMNS = ["title", "product_url", "image_url", "price"]

    @staticmethod
    def validate_csv(csv_file) -> List[str]:
        """
        Validate CSV file format.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Read CSV
            content = csv_file.read().decode("utf-8")
            csv_file.seek(0)  # Reset file pointer
            reader = csv.DictReader(io.StringIO(content))

            # Check required columns
            fieldnames = reader.fieldnames or []
            missing_columns = set(CSVImportService.REQUIRED_COLUMNS) - set(fieldnames)
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")

        except Exception as e:
            errors.append(f"Error reading CSV: {str(e)}")

        return errors

    @staticmethod
    @transaction.atomic
    def import_products(store, csv_file) -> Dict[str, int]:
        """
        Import products from CSV file.

        Returns:
            Dict with counts: {"created": 5, "updated": 0, "errors": 2}
        """
        stats = {"created": 0, "updated": 0, "errors": 0}

        try:
            # Read and parse CSV
            content = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(content))

            # Process each row
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validate required fields
                    if not all(row.get(col) for col in CSVImportService.REQUIRED_COLUMNS):
                        logger.warning(f"Row {row_num}: Missing required fields")
                        stats["errors"] += 1
                        continue

                    # Create product
                    product = Product.objects.create(
                        store=store,
                        title=row["title"].strip(),
                        product_url=row["product_url"].strip(),
                        image_url=row["image_url"].strip(),
                        price=float(row["price"]),
                        tags=row.get("tags", "").strip(),
                        handle=row.get("handle", "").strip(),
                        vendor=row.get("vendor", "").strip(),
                    )
                    stats["created"] += 1

                except ValueError as e:
                    logger.error(f"Row {row_num}: Invalid price value: {e}")
                    stats["errors"] += 1
                except Exception as e:
                    logger.error(f"Row {row_num}: Error creating product: {e}")
                    stats["errors"] += 1

            # Update store metadata
            store.last_synced_at = timezone.now()
            store.integration_type = "CSV"
            store.save()

        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            raise

        return stats
