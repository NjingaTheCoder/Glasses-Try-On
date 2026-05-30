"""
User authentication models.

Implements a custom user model with role-based access control.
- MERCHANT: Can create stores, manage products, view analytics
- CUSTOMER: Can upload photos and generate try-ons
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access.

    Authentication: Token-based (JWT) for stateless API access.
    Why JWT: Scalable, works across multiple services, mobile-friendly.
    """

    class Role(models.TextChoices):
        MERCHANT = "MERCHANT", "Merchant"
        CUSTOMER = "CUSTOMER", "Customer"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Make email the primary login field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def is_merchant(self):
        """Check if user is a merchant."""
        return self.role in [self.Role.MERCHANT, self.Role.ADMIN]

    @property
    def is_customer(self):
        """Check if user is a customer."""
        return self.role == self.Role.CUSTOMER
