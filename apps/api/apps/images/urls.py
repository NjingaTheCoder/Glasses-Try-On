"""
URL patterns for image management.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserImageViewSet

app_name = "images"

router = DefaultRouter()
router.register(r"", UserImageViewSet, basename="userimage")

urlpatterns = [
    path("", include(router.urls)),
]
