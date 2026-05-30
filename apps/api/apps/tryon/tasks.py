"""
Celery tasks for try-on generation.
"""
import logging
import time

from celery import shared_task
from django.utils import timezone

from apps.images.storage import StorageService, generate_generation_image_path

from .models import Generation
from .openai_client import openai_client

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_tryon_generation(self, generation_id: int):
    """
    Run a try-on generation using OpenAI API.

    Steps:
    1. Load generation record and related objects
    2. Check user consent
    3. Get signed URLs for images
    4. Build prompt
    5. Call OpenAI API
    6. Upload result to storage
    7. Update generation record

    Args:
        generation_id: ID of the Generation record
    """
    try:
        # Get generation record
        generation = Generation.objects.select_related(
            "user",
            "user_image",
            "product",
        ).get(id=generation_id)

        # Update status
        generation.status = Generation.Status.PROCESSING
        generation.started_at = timezone.now()
        generation.celery_task_id = self.request.id
        generation.save()

        logger.info(f"Starting generation {generation_id}")

        # Check user consent
        if not generation.user_image.consent_given:
            raise ValueError(
                "User has not given consent for image processing. "
                "Please ensure consent_given=True before generating."
            )

        # Check user image is processed
        if generation.user_image.status != "COMPLETED":
            raise ValueError(
                f"User image is not ready (status: {generation.user_image.status})"
            )

        # Get image URLs
        storage = StorageService()
        user_image_url = storage.generate_download_url(
            generation.user_image.processed_path
        )
        product_image_url = generation.product.image_url

        # Get mask URL if needed (for future implementation)
        mask_url = None
        # TODO: Implement mask support
        # if generation.mask_type:
        #     mask = generation.user_image.masks.filter(mask_type=generation.mask_type).first()
        #     if mask:
        #         mask_url = storage.generate_download_url(mask.mask_path)

        # Call OpenAI API
        start_time = time.time()

        if not openai_client:
            raise ValueError(
                "OpenAI client is not initialized. Please check OPENAI_API_KEY."
            )

        image_data, metadata = openai_client.generate_tryon_image(
            user_image_url=user_image_url,
            product_image_url=product_image_url,
            prompt=generation.prompt,
            mask_url=mask_url,
        )

        # Upload result to storage
        output_path = generate_generation_image_path(
            generation.user_id,
            generation.id,
        )

        storage.upload_file(
            output_path,
            image_data,
            content_type="image/png",
        )

        # Generate signed URL for output
        output_url = storage.generate_download_url(output_path)

        # Update generation record
        generation.output_path = output_path
        generation.output_url = output_url
        generation.status = Generation.Status.SUCCEEDED
        generation.completed_at = timezone.now()
        generation.openai_request_id = metadata.get("request_id", "")
        generation.openai_model = metadata.get("model", "")
        generation.processing_time_seconds = metadata.get("processing_time_seconds", 0)
        generation.save()

        logger.info(
            f"Generation {generation_id} completed successfully in "
            f"{generation.processing_time_seconds:.2f}s"
        )

    except Generation.DoesNotExist:
        logger.error(f"Generation {generation_id} not found")
        raise

    except ValueError as e:
        # Non-retryable errors (consent, invalid state)
        logger.error(f"Generation {generation_id} failed with ValueError: {e}")

        try:
            generation = Generation.objects.get(id=generation_id)
            generation.status = Generation.Status.FAILED
            generation.error_message = str(e)
            generation.completed_at = timezone.now()
            generation.save()
        except Exception:
            pass

        raise

    except Exception as e:
        logger.error(f"Generation {generation_id} failed: {e}")

        # Update status to failed
        try:
            generation = Generation.objects.get(id=generation_id)
            generation.status = Generation.Status.FAILED
            generation.error_message = str(e)
            generation.completed_at = timezone.now()
            generation.save()
        except Exception:
            pass

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** (self.request.retries + 1))
        else:
            raise
