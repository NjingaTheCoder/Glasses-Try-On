"""
URL patterns for webhook handlers.
"""
from django.urls import path

from . import views

app_name = "webhooks"

urlpatterns = [
    # Shopify webhooks
    path(
        "shopify/products-create/",
        views.shopify_products_create,
        name="shopify_products_create",
    ),
    path(
        "shopify/products-update/",
        views.shopify_products_update,
        name="shopify_products_update",
    ),
    path(
        "shopify/products-delete/",
        views.shopify_products_delete,
        name="shopify_products_delete",
    ),
    # Generic webhook for testing
    path("generic/", views.generic_webhook, name="generic"),
]
