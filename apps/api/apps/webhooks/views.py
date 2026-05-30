"""
Webhook handlers for external integrations.

Shopify Webhook Implementation Guide:
--------------------------------------

TODO: Complete Shopify webhook implementation:

1. Webhook Verification:
   - Verify HMAC signature from Shopify
   - Use store's webhook secret
   - Reject invalid requests

2. Webhook Topics to Handle:
   - products/create: New product added
   - products/update: Product updated
   - products/delete: Product deleted
   - shop/update: Store settings changed

3. Implementation Steps:
   a) Add verification function:
      def verify_shopify_webhook(request, secret):
          hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
          data = request.body
          computed_hmac = base64.b64encode(
              hmac.new(secret.encode(), data, hashlib.sha256).digest()
          )
          return hmac.compare_digest(computed_hmac, hmac_header.encode())

   b) Update product handlers to sync data
   c) Handle rate limits and retries
   d) Log all webhook events for debugging

4. Security Considerations:
   - Always verify webhook signature
   - Rate limit webhook endpoints
   - Log suspicious requests
   - Use HTTPS in production

5. Testing:
   - Use Shopify's webhook testing tool
   - Test with ngrok for local development
   - Verify all webhook topics
"""
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def shopify_products_create(request):
    """
    Handle Shopify products/create webhook.

    TODO: Implement webhook verification and product creation logic.

    Expected payload:
    {
        "id": 123456789,
        "title": "Product Title",
        "handle": "product-handle",
        "variants": [...],
        "images": [...]
    }
    """
    # TODO: Verify webhook signature
    # if not verify_shopify_webhook(request, store.shopify_webhook_secret):
    #     return HttpResponse("Invalid signature", status=401)

    # Log the webhook
    logger.info("Received Shopify products/create webhook")

    # TODO: Parse webhook data and create/update product
    # webhook_data = json.loads(request.body)
    # product_id = webhook_data.get('id')
    # ...

    return HttpResponse("OK", status=200)


@csrf_exempt
@require_POST
def shopify_products_update(request):
    """
    Handle Shopify products/update webhook.

    TODO: Implement webhook verification and product update logic.
    """
    logger.info("Received Shopify products/update webhook")

    # TODO: Verify signature and update product

    return HttpResponse("OK", status=200)


@csrf_exempt
@require_POST
def shopify_products_delete(request):
    """
    Handle Shopify products/delete webhook.

    TODO: Implement webhook verification and product deletion logic.
    """
    logger.info("Received Shopify products/delete webhook")

    # TODO: Verify signature and soft-delete product

    return HttpResponse("OK", status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def generic_webhook(request):
    """
    Generic webhook handler for testing.

    This endpoint can be used for testing webhook integrations.
    """
    logger.info(f"Received generic webhook: {request.data}")
    return Response({"status": "received"})


# Helper functions (to be implemented)

def verify_shopify_webhook(request, secret: str) -> bool:
    """
    Verify Shopify webhook HMAC signature.

    Args:
        request: Django request object
        secret: Webhook secret from store settings

    Returns:
        True if signature is valid, False otherwise

    TODO: Implement HMAC verification
    """
    # import base64
    # import hashlib
    # import hmac
    #
    # hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    # if not hmac_header:
    #     return False
    #
    # data = request.body
    # computed_hmac = base64.b64encode(
    #     hmac.new(secret.encode(), data, hashlib.sha256).digest()
    # )
    # return hmac.compare_digest(computed_hmac, hmac_header.encode())

    logger.warning("Webhook verification not implemented - returning True for development")
    return True
