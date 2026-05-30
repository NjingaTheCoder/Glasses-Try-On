"""
URL patterns for store management.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StoreViewSet

app_name = "stores"

router = DefaultRouter()
router.register(r"", StoreViewSet, basename="store")

urlpatterns = [
    path("", include(router.urls)),
]
