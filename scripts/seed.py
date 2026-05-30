#!/usr/bin/env python
"""
Seed script for WearLens database.

Creates sample data for development and testing:
- A merchant user
- A customer user
- A sample store
- Sample products (from CSV)
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.stores.services import CSVImportService

User = get_user_model()


def seed():
    """Seed the database with sample data."""
    print("🌱 Seeding database...")

    # Create merchant user
    merchant, created = User.objects.get_or_create(
        email="merchant@wearlens.com",
        defaults={
            "username": "merchant",
            "role": User.Role.MERCHANT,
            "first_name": "John",
            "last_name": "Merchant",
        }
    )
    if created:
        merchant.set_password("merchant123")
        merchant.save()
        print(f"✓ Created merchant user: {merchant.email}")
    else:
        print(f"→ Merchant user already exists: {merchant.email}")

    # Create customer user
    customer, created = User.objects.get_or_create(
        email="customer@wearlens.com",
        defaults={
            "username": "customer",
            "role": User.Role.CUSTOMER,
            "first_name": "Jane",
            "last_name": "Customer",
        }
    )
    if created:
        customer.set_password("customer123")
        customer.save()
        print(f"✓ Created customer user: {customer.email}")
    else:
        print(f"→ Customer user already exists: {customer.email}")

    # Create sample store
    store, created = Store.objects.get_or_create(
        owner=merchant,
        name="Sample Fashion Store",
        defaults={
            "description": "A sample store with demo products for testing virtual try-on",
            "integration_type": Store.IntegrationType.CSV,
        }
    )
    if created:
        print(f"✓ Created store: {store.name}")
    else:
        print(f"→ Store already exists: {store.name}")

    # Import sample products from CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'sample_products.csv')

    if os.path.exists(csv_path):
        # Check if products already exist
        if store.products.count() == 0:
            print(f"📦 Importing products from {csv_path}")

            with open(csv_path, 'rb') as csv_file:
                try:
                    stats = CSVImportService.import_products(store, csv_file)
                    print(f"✓ Imported {stats['created']} products")
                    if stats['errors'] > 0:
                        print(f"⚠ {stats['errors']} products failed to import")
                except Exception as e:
                    print(f"✗ Failed to import products: {e}")
        else:
            print(f"→ Store already has {store.products.count()} products")
    else:
        print(f"⚠ CSV file not found at {csv_path}")

    print("\n" + "="*50)
    print("🎉 Seeding complete!")
    print("="*50)
    print("\nTest Credentials:")
    print("\nMerchant Account:")
    print(f"  Email: {merchant.email}")
    print("  Password: merchant123")
    print("\nCustomer Account:")
    print(f"  Email: {customer.email}")
    print("  Password: customer123")
    print("\nAccess the application at: http://localhost:5173")
    print("Access Django admin at: http://localhost:8000/admin")
    print("="*50 + "\n")


if __name__ == "__main__":
    seed()
