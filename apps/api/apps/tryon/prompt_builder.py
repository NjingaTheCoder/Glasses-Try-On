"""
Centralized prompt builder for virtual try-on.

This module contains the prompt templates and logic for generating
effective prompts for the OpenAI image editing API.
"""
from typing import Optional


class TryOnPromptBuilder:
    """
    Builder for virtual try-on prompts.

    Generates consistent, effective prompts for OpenAI's image editing API.
    """

    # Base template for garment try-on
    BASE_TEMPLATE = """Edit the first image (full-body person photo) so the person is wearing the garment shown in the second image.

PRESERVE:
- Identity, face, facial features, expression
- Hair style, hair color, hair texture
- Body shape, proportions, physique
- Skin tone and texture
- Pose and body position
- Background and environment
- Lighting conditions and shadows
- Camera perspective and angle

CHANGE:
- Replace the {garment_area} clothing with the exact garment from the second image
- Match the garment's color, material, pattern, texture precisely
- Match logo placement, branding, graphics exactly
- Match neckline, collar, sleeves, hem, fit, and cut accurately
- Add realistic wrinkles, folds, and fabric drape
- Add proper shadows and occlusions where garment overlaps body
- Ensure garment fits naturally on the person's body

REQUIREMENTS:
- Photorealistic quality
- Natural lighting consistency
- Seamless integration of garment
- No visible editing artifacts
- Maintain original image resolution and quality
- Do not change the person's face or facial features
"""

    GARMENT_AREA_MAP = {
        "UPPER_BODY": "upper body (torso, chest, shoulders, arms)",
        "LOWER_BODY": "lower body (legs, hips, waist)",
        "FULL_BODY": "entire body",
        "DRESS": "entire body dress/outfit",
        "OUTERWEAR": "outerwear (jacket, coat)",
    }

    def build_prompt(
        self,
        garment_type: str = "UPPER_BODY",
        additional_instructions: Optional[str] = None,
    ) -> str:
        """
        Build a prompt for virtual try-on.

        Args:
            garment_type: Type of garment (UPPER_BODY, LOWER_BODY, etc.)
            additional_instructions: Optional additional instructions

        Returns:
            Complete prompt string
        """
        # Get garment area description
        garment_area = self.GARMENT_AREA_MAP.get(
            garment_type,
            self.GARMENT_AREA_MAP["UPPER_BODY"],
        )

        # Build base prompt
        prompt = self.BASE_TEMPLATE.format(garment_area=garment_area)

        # Add additional instructions if provided
        if additional_instructions:
            prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{additional_instructions}"

        return prompt.strip()

    def build_product_specific_prompt(
        self,
        product_title: str,
        product_tags: list,
        garment_type: str = "UPPER_BODY",
    ) -> str:
        """
        Build a prompt with product-specific information.

        Args:
            product_title: Title of the product
            product_tags: List of product tags
            garment_type: Type of garment

        Returns:
            Complete prompt string
        """
        # Detect garment type from tags if not specified
        if not garment_type or garment_type == "UPPER_BODY":
            garment_type = self._detect_garment_type(product_title, product_tags)

        # Build base prompt
        prompt = self.build_prompt(garment_type=garment_type)

        # Add product-specific context
        additional_context = f"\nPRODUCT: {product_title}"
        if product_tags:
            additional_context += f"\nTAGS: {', '.join(product_tags)}"

        prompt += additional_context

        return prompt

    def _detect_garment_type(self, product_title: str, product_tags: list) -> str:
        """
        Detect garment type from product title and tags.

        Args:
            product_title: Product title
            product_tags: List of tags

        Returns:
            Garment type string
        """
        title_lower = product_title.lower()
        tags_lower = [tag.lower() for tag in product_tags]
        all_text = f"{title_lower} {' '.join(tags_lower)}"

        # Check for specific garment types
        if any(
            keyword in all_text
            for keyword in ["dress", "gown", "jumpsuit", "romper"]
        ):
            return "DRESS"

        if any(
            keyword in all_text
            for keyword in ["jacket", "coat", "blazer", "cardigan", "hoodie"]
        ):
            return "OUTERWEAR"

        if any(
            keyword in all_text
            for keyword in ["pants", "jeans", "shorts", "skirt", "trousers"]
        ):
            return "LOWER_BODY"

        # Default to upper body for shirts, t-shirts, etc.
        return "UPPER_BODY"


# Global instance
prompt_builder = TryOnPromptBuilder()
