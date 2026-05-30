"""
Celery tasks for image processing.
"""
import logging

import requests
from celery import shared_task
from django.utils import timezone

from .models import UserImage
from .processors import ImageProcessor
from .storage import StorageService, generate_user_image_path

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_user_image(self, user_image_id: int):
    """
    Process a user-uploaded image.

    Steps:
    1. Download original image from storage
    2. Normalize EXIF orientation
    3. Resize to target dimensions
    4. Upload processed image back to storage
    5. Update UserImage record

    Args:
        user_image_id: ID of the UserImage record
    """
    try:
        # Get the image record
        user_image = UserImage.objects.get(id=user_image_id)
        user_image.status = UserImage.ProcessingStatus.PROCESSING
        user_image.save()

        logger.info(f"Processing user image {user_image_id}")

        # Initialize services
        storage = StorageService()
        processor = ImageProcessor()

        # Download original image
        original_data = storage.download_file(user_image.original_path)

        # Process image
        processed_data, metadata = processor.process_user_image(original_data)

        # Generate path for processed image
        processed_path = generate_user_image_path(
            user_image.user_id,
            "processed.png",
            prefix="processed",
        )

        # Upload processed image
        storage.upload_file(
            processed_path,
            processed_data,
            content_type=metadata["mime_type"],
        )

        # Generate signed URL for processed image
        processed_url = storage.generate_download_url(processed_path)

        # Update record
        user_image.processed_path = processed_path
        user_image.processed_url = processed_url
        user_image.original_width = metadata["original_width"]
        user_image.original_height = metadata["original_height"]
        user_image.processed_width = metadata["processed_width"]
        user_image.processed_height = metadata["processed_height"]
        user_image.file_size = metadata["file_size"]
        user_image.mime_type = metadata["mime_type"]
        user_image.status = UserImage.ProcessingStatus.COMPLETED
        user_image.processed_at = timezone.now()
        user_image.save()

        logger.info(f"Successfully processed user image {user_image_id}")

    except UserImage.DoesNotExist:
        logger.error(f"UserImage {user_image_id} not found")
        raise

    except Exception as e:
        logger.error(f"Error processing user image {user_image_id}: {e}")

        # Update status to failed
        try:
            user_image = UserImage.objects.get(id=user_image_id)
            user_image.status = UserImage.ProcessingStatus.FAILED
            user_image.error_message = str(e)
            user_image.save()
        except Exception:
            pass

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2**self.request.retries)


@shared_task(bind=True, max_retries=3)
def fetch_and_cache_product_image(self, product_image_url: str, storage_path: str):
    """
    Download and cache a product image.

    Args:
        product_image_url: URL of the product image
        storage_path: Path to store the image in S3/MinIO
    """
    try:
        logger.info(f"Fetching product image: {product_image_url}")

        # Download image
        response = requests.get(product_image_url, timeout=30)
        response.raise_for_status()
        image_data = response.content

        # Process image
        processor = ImageProcessor()
        processed_data, metadata = processor.process_product_image(image_data)

        # Upload to storage
        storage = StorageService()
        storage.upload_file(
            storage_path,
            processed_data,
            content_type=metadata["mime_type"],
        )

        logger.info(f"Successfully cached product image at {storage_path}")

    except Exception as e:
        logger.error(f"Error caching product image: {e}")
        raise self.retry(exc=e, countdown=2**self.request.retries)
