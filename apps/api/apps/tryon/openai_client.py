"""
OpenAI API client for image generation.

Handles communication with OpenAI's image editing API with proper
error handling, retries, and timeout management.
"""
import logging
import time
from typing import Optional, Tuple

import requests
from django.conf import settings
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client for OpenAI image editing API.

    Provides retry logic, error handling, and timeout management.
    """

    def __init__(self):
        """Initialize OpenAI client with configuration from settings."""
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not configured. Please set it in your environment."
            )

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=settings.OPENAI_TIMEOUT,
            max_retries=0,  # We handle retries manually
        )
        self.model = settings.OPENAI_MODEL
        self.max_retries = settings.OPENAI_MAX_RETRIES

    def generate_tryon_image(
        self,
        user_image_url: str,
        product_image_url: str,
        prompt: str,
        mask_url: Optional[str] = None,
    ) -> Tuple[bytes, dict]:
        """
        Generate a try-on image using OpenAI's image editing API.

        Args:
            user_image_url: URL of the user's photo
            product_image_url: URL of the product image
            prompt: Generation prompt
            mask_url: Optional mask image URL

        Returns:
            Tuple of (image_bytes, metadata_dict)

        Raises:
            OpenAIError: If generation fails after retries
        """
        # Download images
        user_image_data = self._download_image(user_image_url)
        product_image_data = self._download_image(product_image_url)
        mask_data = self._download_image(mask_url) if mask_url else None

        # Prepare for retry logic
        last_exception = None
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Attempting OpenAI image generation (attempt {attempt + 1}/{self.max_retries + 1})"
                )

                # Call OpenAI API
                # Note: The actual API endpoint and parameters may vary
                # This is a placeholder for the image editing API
                response = self.client.images.edit(
                    image=user_image_data,
                    prompt=prompt,
                    n=1,
                    size="1024x1024",  # Adjust as needed
                )

                # Get the generated image URL
                generated_image_url = response.data[0].url

                # Download generated image
                generated_image_data = self._download_image(generated_image_url)

                # Calculate processing time
                processing_time = time.time() - start_time

                # Prepare metadata
                metadata = {
                    "request_id": response.id if hasattr(response, "id") else None,
                    "model": self.model,
                    "processing_time_seconds": processing_time,
                    "revised_prompt": getattr(response.data[0], "revised_prompt", None),
                }

                logger.info(
                    f"Successfully generated image in {processing_time:.2f}s"
                )

                return generated_image_data, metadata

            except OpenAIError as e:
                last_exception = e
                logger.warning(
                    f"OpenAI API error (attempt {attempt + 1}): {e}"
                )

                # Don't retry on certain errors
                if self._is_non_retryable_error(e):
                    logger.error(f"Non-retryable error: {e}")
                    raise

                # Exponential backoff
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error during generation: {e}")

                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    time.sleep(wait_time)

        # All retries failed
        logger.error(f"All retry attempts failed. Last error: {last_exception}")
        raise last_exception

    def _download_image(self, url: str) -> bytes:
        """
        Download an image from a URL.

        Args:
            url: Image URL

        Returns:
            Image data as bytes

        Raises:
            requests.RequestException: If download fails
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Error downloading image from {url}: {e}")
            raise

    def _is_non_retryable_error(self, error: OpenAIError) -> bool:
        """
        Check if an error should not be retried.

        Args:
            error: OpenAI error

        Returns:
            True if error should not be retried
        """
        # Check error type and status code
        error_str = str(error).lower()

        # Don't retry on authentication errors
        if "authentication" in error_str or "unauthorized" in error_str:
            return True

        # Don't retry on invalid request errors
        if "invalid" in error_str or "bad request" in error_str:
            return True

        # Don't retry on content policy violations
        if "content_policy" in error_str or "safety" in error_str:
            return True

        # Retry on rate limits and server errors
        return False


# Global client instance
openai_client = OpenAIClient() if settings.OPENAI_API_KEY else None
