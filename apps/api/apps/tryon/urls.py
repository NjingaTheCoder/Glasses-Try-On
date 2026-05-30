"""
URL patterns for try-on generation.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GenerationViewSet, TryOnSessionViewSet, TryOnViewSet

app_name = "tryon"

router = DefaultRouter()
router.register(r"", TryOnViewSet, basename="tryon")

# Note: Generations have their own endpoint
urlpatterns = [
    path("", include(router.urls)),
]

# Add generation routes separately (accessed via /api/generations/)
generation_router = DefaultRouter()
generation_router.register(r"generations", GenerationViewSet, basename="generation")

# Add session routes
session_router = DefaultRouter()
session_router.register(r"sessions", TryOnSessionViewSet, basename="session")
