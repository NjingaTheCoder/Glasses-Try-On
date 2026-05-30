"""
Authentication views for user registration, login, and profile management.
"""
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    POST /api/auth/register/
    {
        "email": "user@example.com",
        "username": "username",
        "password": "password123",
        "password_confirm": "password123",
        "role": "CUSTOMER"  // or "MERCHANT"
    }
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User registered successfully. Please login.",
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LoginView(TokenObtainPairView):
    """
    API endpoint for user login.

    POST /api/auth/login/
    {
        "email": "user@example.com",
        "password": "password123"
    }

    Returns JWT access and refresh tokens along with user details.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    API endpoint for user logout.

    POST /api/auth/logout/

    Note: With JWT, logout is primarily handled client-side by removing tokens.
    This endpoint is provided for consistency and can be extended to blacklist tokens.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # TODO: Add token blacklisting if needed
        # For now, logout is handled client-side by removing tokens
        return Response(
            {"message": "Logged out successfully. Please remove tokens from client."},
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update user profile.

    GET /api/auth/profile/
    PATCH /api/auth/profile/
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
