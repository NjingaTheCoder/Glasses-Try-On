"""
Image processing utilities.

Handles image normalization, resizing, and format conversion.
"""
import io
import logging
from typing import Tuple

from django.conf import settings
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image processing service for user uploads.

    Handles:
    - EXIF orientation normalization
    - Resizing to target dimensions
    - Format conversion
    - Quality optimization
    """

    def __init__(
        self,
        max_size: int = None,
        output_format: str = None,
        quality: int = None,
    ):
        """
        Initialize processor with configuration.

        Args:
            max_size: Maximum dimension (width or height)
            output_format: Output format (PNG, JPEG)
            quality: JPEG quality (1-100)
        """
        self.max_size = max_size or settings.IMAGE_MAX_SIZE
        self.output_format = output_format or settings.IMAGE_FORMAT
        self.quality = quality or settings.IMAGE_QUALITY

    def process_user_image(self, image_data: bytes) -> Tuple[bytes, dict]:
        """
        Process a user-uploaded image.

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (processed_image_bytes, metadata_dict)
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))

            # Store original dimensions
            original_width, original_height = image.size

            # Normalize EXIF orientation
            image = ImageOps.exif_transpose(image)

            # Convert to RGB if necessary (for PNG with alpha, etc.)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")

            # Resize maintaining aspect ratio
            image = self._resize_image(image, self.max_size)

            # Get new dimensions
            processed_width, processed_height = image.size

            # Convert to output format
            output = io.BytesIO()
            save_kwargs = {"format": self.output_format}

            if self.output_format == "JPEG":
                save_kwargs["quality"] = self.quality
                save_kwargs["optimize"] = True
                # Convert RGBA to RGB for JPEG
                if image.mode == "RGBA":
                    image = image.convert("RGB")
            elif self.output_format == "PNG":
                save_kwargs["optimize"] = True

            image.save(output, **save_kwargs)
            processed_data = output.getvalue()

            # Prepare metadata
            metadata = {
                "original_width": original_width,
                "original_height": original_height,
                "processed_width": processed_width,
                "processed_height": processed_height,
                "file_size": len(processed_data),
                "mime_type": f"image/{self.output_format.lower()}",
            }

            logger.info(
                f"Processed image: {original_width}x{original_height} -> "
                f"{processed_width}x{processed_height}"
            )

            return processed_data, metadata

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    def process_product_image(self, image_data: bytes) -> Tuple[bytes, dict]:
        """
        Process a product image (downloaded from URL).

        Similar to user image processing but may have different constraints.

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (processed_image_bytes, metadata_dict)
        """
        # Use same logic as user images for now
        return self.process_user_image(image_data)

    def _resize_image(self, image: Image.Image, max_size: int) -> Image.Image:
        """
        Resize image maintaining aspect ratio.

        Args:
            image: PIL Image object
            max_size: Maximum dimension

        Returns:
            Resized PIL Image
        """
        width, height = image.size

        # Calculate new dimensions
        if width > height:
            if width > max_size:
                new_width = max_size
                new_height = int((height / width) * max_size)
            else:
                return image
        else:
            if height > max_size:
                new_height = max_size
                new_width = int((width / height) * max_size)
            else:
                return image

        # Resize with high-quality resampling
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized

    def generate_simple_mask(
        self,
        image_data: bytes,
        mask_type: str = "UPPER_BODY",
    ) -> bytes:
        """
        Generate a simple placeholder mask.

        TODO: Replace with actual segmentation model (SAM, U-Net, etc.)

        For MVP, this creates a basic rectangular mask based on mask type.

        Args:
            image_data: Original image bytes
            mask_type: Type of mask (UPPER_BODY, LOWER_BODY, FULL_BODY)

        Returns:
            Mask image bytes (white = keep, black = change)
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size

            # Create a white mask (all ones)
            mask = Image.new("L", (width, height), 255)

            # TODO: Implement proper segmentation
            # For now, create a simple rectangular mask
            if mask_type == "UPPER_BODY":
                # Top half of the image
                from PIL import ImageDraw

                draw = ImageDraw.Draw(mask)
                # Black rectangle for upper body (will be changed)
                draw.rectangle(
                    [(width * 0.2, height * 0.1), (width * 0.8, height * 0.6)],
                    fill=0,
                )

            # Save mask
            output = io.BytesIO()
            mask.save(output, format="PNG")
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error generating mask: {e}")
            raise


def remove_background(image_data: bytes) -> bytes:
    """
    Remove background from product image.

    TODO: Implement background removal (rembg, U2Net, etc.)

    For MVP, this is a placeholder that returns the original image.

    Args:
        image_data: Original image bytes

    Returns:
        Image bytes with background removed
    """
    logger.warning("Background removal not implemented, returning original image")
    return image_data
