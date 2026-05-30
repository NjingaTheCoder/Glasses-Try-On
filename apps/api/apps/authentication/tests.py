"""
Tests for authentication app.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

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


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration."""

    def test_register_customer(self, api_client):
        """Test customer registration."""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "role": "CUSTOMER",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_register_merchant(self, api_client):
        """Test merchant registration."""
        data = {
            "email": "newmerchant@example.com",
            "username": "newmerchant",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "role": "MERCHANT",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email="newmerchant@example.com")
        assert user.role == User.Role.MERCHANT

    def test_register_password_mismatch(self, api_client):
        """Test registration with password mismatch."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "password_confirm": "different",
            "role": "CUSTOMER",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test user login."""

    def test_login_success(self, api_client, customer_user):
        """Test successful login."""
        data = {"email": "customer@example.com", "password": "testpass123"}
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

    def test_login_invalid_credentials(self, api_client, customer_user):
        """Test login with invalid credentials."""
        data = {"email": "customer@example.com", "password": "wrongpassword"}
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_profile_authenticated(self, api_client, customer_user):
        """Test getting profile when authenticated."""
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == customer_user.email

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated."""
        response = api_client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
