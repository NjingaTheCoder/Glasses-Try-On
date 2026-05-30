"""
Views for try-on generation.
"""
import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from apps.images.models import UserImage
from apps.products.models import Product

from .models import Generation, GenerationFeedback, TryOnSession
from .prompt_builder import prompt_builder
from .serializers import (
    CreateGenerationSerializer,
    GenerationFeedbackSerializer,
    GenerationSerializer,
    TryOnSessionSerializer,
)
from .tasks import run_tryon_generation

logger = logging.getLogger(__name__)


class TryOnRateThrottle(UserRateThrottle):
    """Custom rate throttle for try-on generation."""

    scope = "tryon"


class TryOnViewSet(viewsets.ViewSet):
    """
    ViewSet for try-on generation.

    create: POST /api/tryon/ - Create a new generation
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [TryOnRateThrottle]

    def create(self, request):
        """
        Create a new try-on generation.

        POST /api/tryon/
        {
            "user_image_id": 123,
            "product_id": 456,
            "session_id": 789,  // optional
            "mask_type": "UPPER_BODY"  // optional
        }

        Rate limited to 10 requests per hour per user.
        """
        serializer = CreateGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_image_id = serializer.validated_data["user_image_id"]
        product_id = serializer.validated_data["product_id"]
        session_id = serializer.validated_data.get("session_id")
        mask_type = serializer.validated_data.get("mask_type", "UPPER_BODY")

        try:
            # Validate user_image belongs to user
            user_image = UserImage.objects.get(
                id=user_image_id,
                user=request.user,
            )

            # Check consent
            if not user_image.consent_given:
                return Response(
                    {
                        "error": "User consent required. "
                        "Please ensure consent_given=True on the user image."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check image is processed
            if user_image.status != UserImage.ProcessingStatus.COMPLETED:
                return Response(
                    {
                        "error": f"User image is not ready. Current status: {user_image.status}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate product exists
            product = Product.objects.get(id=product_id, is_active=True)

            # Get or validate session
            session = None
            if session_id:
                try:
                    session = TryOnSession.objects.get(
                        id=session_id,
                        user=request.user,
                    )
                except TryOnSession.DoesNotExist:
                    return Response(
                        {"error": "Session not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # Build prompt
            prompt = prompt_builder.build_product_specific_prompt(
                product_title=product.title,
                product_tags=product.tag_list,
                garment_type=mask_type,
            )

            # Create generation record
            generation = Generation.objects.create(
                user=request.user,
                user_image=user_image,
                product=product,
                session=session,
                prompt=prompt,
                mask_type=mask_type,
                status=Generation.Status.QUEUED,
            )

            # Trigger async processing
            task = run_tryon_generation.delay(generation.id)
            generation.celery_task_id = task.id
            generation.save(update_fields=["celery_task_id"])

            logger.info(
                f"Created generation {generation.id} for user {request.user.id}"
            )

            return Response(
                {
                    "message": "Generation queued successfully",
                    "generation": GenerationSerializer(generation).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except UserImage.DoesNotExist:
            return Response(
                {"error": "User image not found or does not belong to you"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found or inactive"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            logger.error(f"Error creating generation: {e}")
            return Response(
                {"error": "Failed to create generation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing generations.

    list:     GET /api/generations/?session_id=123
    retrieve: GET /api/generations/{id}/
    """

    serializer_class = GenerationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return generations for current user, optionally filtered by session."""
        queryset = Generation.objects.filter(user=self.request.user).select_related(
            "user",
            "product",
            "user_image",
        )

        # Filter by session if provided
        session_id = self.request.query_params.get("session_id")
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        # Filter by status if provided
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=["post"])
    def feedback(self, request, pk=None):
        """
        Add feedback to a generation.

        POST /api/generations/{id}/feedback/
        {
            "rating": 4,
            "comment": "Great result!"
        }
        """
        generation = self.get_object()

        serializer = GenerationFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create or update feedback
        feedback, created = GenerationFeedback.objects.update_or_create(
            generation=generation,
            defaults={
                "rating": serializer.validated_data["rating"],
                "comment": serializer.validated_data.get("comment", ""),
            },
        )

        return Response(
            {
                "message": "Feedback saved",
                "feedback": GenerationFeedbackSerializer(feedback).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TryOnSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for try-on sessions.

    list:    GET /api/sessions/
    create:  POST /api/sessions/
    retrieve: GET /api/sessions/{id}/
    """

    serializer_class = TryOnSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return sessions for current user."""
        return TryOnSession.objects.filter(user=self.request.user).prefetch_related(
            "generations"
        )

    def create(self, request, *args, **kwargs):
        """Create a new session."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set user to current user
        session = serializer.save(user=request.user)

        return Response(
            self.get_serializer(session).data,
            status=status.HTTP_201_CREATED,
        )
