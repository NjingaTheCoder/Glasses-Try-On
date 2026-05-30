"""
S3/MinIO storage utilities for image management.
"""
import logging
from datetime import timedelta
from typing import Optional, Tuple

from django.conf import settings
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class StorageService:
    """
    Service for S3/MinIO storage operations.

    Handles uploads, downloads, and signed URL generation.
    """

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise

    def generate_upload_url(
        self,
        object_path: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        """
        Generate a presigned URL for uploading.

        Args:
            object_path: Path in bucket (e.g., "users/123/image.jpg")
            expires: URL expiration time

        Returns:
            Presigned upload URL
        """
        try:
            url = self.client.presigned_put_object(
                self.bucket_name,
                object_path,
                expires=expires,
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating upload URL: {e}")
            raise

    def generate_download_url(
        self,
        object_path: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        """
        Generate a presigned URL for downloading.

        Args:
            object_path: Path in bucket
            expires: URL expiration time

        Returns:
            Presigned download URL
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_path,
                expires=expires,
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating download URL: {e}")
            raise

    def upload_file(self, object_path: str, file_data: bytes, content_type: str = "image/jpeg"):
        """
        Upload a file directly to storage.

        Args:
            object_path: Path in bucket
            file_data: File data as bytes
            content_type: MIME type
        """
        try:
            from io import BytesIO

            self.client.put_object(
                self.bucket_name,
                object_path,
                BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            logger.info(f"Uploaded file to {object_path}")
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    def download_file(self, object_path: str) -> bytes:
        """
        Download a file from storage.

        Args:
            object_path: Path in bucket

        Returns:
            File data as bytes
        """
        try:
            response = self.client.get_object(self.bucket_name, object_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise

    def delete_file(self, object_path: str):
        """
        Delete a file from storage.

        Args:
            object_path: Path in bucket
        """
        try:
            self.client.remove_object(self.bucket_name, object_path)
            logger.info(f"Deleted file: {object_path}")
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise

    def file_exists(self, object_path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            object_path: Path in bucket

        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket_name, object_path)
            return True
        except S3Error:
            return False

    def get_file_size(self, object_path: str) -> Optional[int]:
        """
        Get the size of a file in bytes.

        Args:
            object_path: Path in bucket

        Returns:
            File size in bytes or None if not found
        """
        try:
            stat = self.client.stat_object(self.bucket_name, object_path)
            return stat.size
        except S3Error:
            return None


def generate_user_image_path(user_id: int, filename: str, prefix: str = "original") -> str:
    """
    Generate a path for user image storage.

    Args:
        user_id: User ID
        filename: Original filename
        prefix: Prefix (original, processed, mask)

    Returns:
        Storage path like "users/123/original/abc123.jpg"
    """
    import uuid

    extension = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    unique_id = uuid.uuid4().hex[:12]
    return f"users/{user_id}/{prefix}/{unique_id}.{extension}"


def generate_product_image_path(product_id: int, filename: str) -> str:
    """
    Generate a path for cached product image.

    Args:
        product_id: Product ID
        filename: Original filename

    Returns:
        Storage path like "products/456/abc123.jpg"
    """
    import uuid

    extension = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    unique_id = uuid.uuid4().hex[:12]
    return f"products/{product_id}/{unique_id}.{extension}"


def generate_generation_image_path(user_id: int, generation_id: int) -> str:
    """
    Generate a path for generation output image.

    Args:
        user_id: User ID
        generation_id: Generation ID

    Returns:
        Storage path like "generations/123/456/result.png"
    """
    return f"generations/{user_id}/{generation_id}/result.png"
