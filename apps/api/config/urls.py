"""
URL configuration for WearLens project.
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from apps.tryon.views import GenerationViewSet, TryOnSessionViewSet

# Create a router for API endpoints
router = routers.DefaultRouter()
router.register(r"generations", GenerationViewSet, basename="generation")
router.register(r"sessions", TryOnSessionViewSet, basename="session")

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/", include(router.urls)),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/stores/", include("apps.stores.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/user-images/", include("apps.images.urls")),
    path("api/tryon/", include("apps.tryon.urls")),
    path("api/webhooks/", include("apps.webhooks.urls")),
]
