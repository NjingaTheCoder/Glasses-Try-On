"""
Tests for stores app.
"""
import io

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from .models import Store

User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.fixture
def merchant_user(db):
    """Create a merchant user."""
    return User.objects.create_user(
        email="merchant@example.com",
        username="merchant",
        password="testpass123",
        role=User.Role.MERCHANT,
    )


@pytest.fixture
def customer_user(db):
    """Create a customer user."""
    return User.objects.create_user(
        email="customer@example.com",
        username="customer",
        password="testpass123",
        role=User.Role.CUSTOMER,
    )


@pytest.fixture
def store(merchant_user):
    """Create a test store."""
    return Store.objects.create(
        owner=merchant_user,
        name="Test Store",
        description="A test store",
    )


@pytest.mark.django_db
class TestStoreViewSet:
    """Test store CRUD operations."""

    def test_create_store(self, api_client, merchant_user):
        """Test creating a store."""
        api_client.force_authenticate(user=merchant_user)
        data = {
            "name": "New Store",
            "description": "My new store",
        }
        response = api_client.post("/api/stores/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Store.objects.filter(name="New Store").exists()

    def test_list_stores_merchant(self, api_client, merchant_user, store):
        """Test listing stores as merchant."""
        api_client.force_authenticate(user=merchant_user)
        response = api_client.get("/api/stores/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_list_stores_customer(self, api_client, customer_user, store):
        """Test that customers only see their own stores."""
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/stores/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_csv_import_valid(self, api_client, merchant_user, store):
        """Test CSV import with valid data."""
        api_client.force_authenticate(user=merchant_user)

        # Create a sample CSV file
        csv_content = """title,product_url,image_url,price,tags
T-Shirt,https://example.com/tshirt,https://example.com/tshirt.jpg,29.99,clothing
Jeans,https://example.com/jeans,https://example.com/jeans.jpg,59.99,clothing
"""
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "products.csv"

        response = api_client.post(
            f"/api/stores/{store.id}/csv-import/",
            {"csv_file": csv_file},
            format="multipart",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["stats"]["created"] == 2

    def test_csv_import_invalid_format(self, api_client, merchant_user, store):
        """Test CSV import with invalid format."""
        api_client.force_authenticate(user=merchant_user)

        # Create CSV with missing required columns
        csv_content = """title,price
T-Shirt,29.99
"""
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "products.csv"

        response = api_client.post(
            f"/api/stores/{store.id}/csv-import/",
            {"csv_file": csv_file},
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
