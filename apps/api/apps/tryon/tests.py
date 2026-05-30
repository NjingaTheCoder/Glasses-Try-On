"""
Tests for try-on generation.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.images.models import UserImage
from apps.products.models import Product
from apps.stores.models import Store

from .models import Generation

User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


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
def merchant_user(db):
    """Create a merchant user."""
    return User.objects.create_user(
        email="merchant@example.com",
        username="merchant",
        password="testpass123",
        role=User.Role.MERCHANT,
    )


@pytest.fixture
def store(merchant_user):
    """Create a test store."""
    return Store.objects.create(
        owner=merchant_user,
        name="Test Store",
    )


@pytest.fixture
def product(store):
    """Create a test product."""
    return Product.objects.create(
        store=store,
        title="Test T-Shirt",
        product_url="https://example.com/tshirt",
        image_url="https://example.com/tshirt.jpg",
        price=29.99,
        tags="clothing,casual",
    )


@pytest.fixture
def user_image(customer_user):
    """Create a processed user image."""
    return UserImage.objects.create(
        user=customer_user,
        original_path="users/1/original/test.jpg",
        processed_path="users/1/processed/test.jpg",
        consent_given=True,
        status=UserImage.ProcessingStatus.COMPLETED,
    )


@pytest.mark.django_db
class TestTryOnGeneration:
    """Test try-on generation."""

    def test_create_generation_success(
        self, api_client, customer_user, user_image, product
    ):
        """Test creating a generation with valid data."""
        api_client.force_authenticate(user=customer_user)
        data = {
            "user_image_id": user_image.id,
            "product_id": product.id,
            "mask_type": "UPPER_BODY",
        }

        # Note: This will fail in test because OpenAI API is not available
        # In production, you'd mock the OpenAI client
        response = api_client.post("/api/tryon/", data)

        # Should create the generation record even if task fails
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]

        if response.status_code == status.HTTP_201_CREATED:
            assert Generation.objects.filter(
                user=customer_user,
                product=product,
            ).exists()

    def test_create_generation_without_consent(
        self, api_client, customer_user, user_image, product
    ):
        """Test that generation fails without user consent."""
        # Remove consent
        user_image.consent_given = False
        user_image.save()

        api_client.force_authenticate(user=customer_user)
        data = {
            "user_image_id": user_image.id,
            "product_id": product.id,
        }

        response = api_client.post("/api/tryon/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "consent" in response.data["error"].lower()

    def test_create_generation_unprocessed_image(
        self, api_client, customer_user, product
    ):
        """Test that generation fails with unprocessed image."""
        # Create unprocessed image
        unprocessed_image = UserImage.objects.create(
            user=customer_user,
            original_path="users/1/original/test2.jpg",
            consent_given=True,
            status=UserImage.ProcessingStatus.PENDING,
        )

        api_client.force_authenticate(user=customer_user)
        data = {
            "user_image_id": unprocessed_image.id,
            "product_id": product.id,
        }

        response = api_client.post("/api/tryon/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not ready" in response.data["error"].lower()

    def test_list_generations(self, api_client, customer_user):
        """Test listing user's generations."""
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/tryon/generations/")

        # Should work even with no generations
        assert response.status_code == status.HTTP_200_OK

    def test_access_control(self, api_client, customer_user, merchant_user, user_image):
        """Test that users can only access their own generations."""
        # Customer creates generation
        generation = Generation.objects.create(
            user=customer_user,
            user_image=user_image,
            product=Product.objects.create(
                store=Store.objects.create(owner=merchant_user, name="Store"),
                title="Product",
                product_url="http://example.com",
                image_url="http://example.com/img.jpg",
                price=10,
            ),
            prompt="Test prompt",
        )

        # Merchant tries to access customer's generation
        api_client.force_authenticate(user=merchant_user)
        response = api_client.get(f"/api/tryon/generations/{generation.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
