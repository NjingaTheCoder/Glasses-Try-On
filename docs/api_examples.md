# API Examples

Complete API documentation with curl examples and response formats.

## Base URL

```
http://localhost:8000/api
```

## Authentication

### Register

Create a new user account.

**Endpoint:** `POST /auth/register/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "CUSTOMER"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "User registered successfully. Please login."
}
```

### Login

Authenticate and receive JWT tokens.

**Endpoint:** `POST /auth/login/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "role": "CUSTOMER"
  }
}
```

### Get Profile

Get current user information.

**Endpoint:** `GET /auth/profile/`

**Request:**
```bash
curl http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "role": "CUSTOMER",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Stores

### List Stores

Get all stores for the current user.

**Endpoint:** `GET /stores/`

**Request:**
```bash
curl http://localhost:8000/api/stores/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Fashion Store",
      "description": "My fashion store",
      "integration_type": "CSV",
      "shopify_domain": "",
      "owner": 1,
      "owner_email": "merchant@example.com",
      "product_count": 25,
      "is_active": true,
      "last_synced_at": "2024-01-15T12:00:00Z",
      "created_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

### Create Store

Create a new store.

**Endpoint:** `POST /stores/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/stores/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Store",
    "description": "A store for trendy clothing"
  }'
```

**Response:**
```json
{
  "id": 2,
  "name": "My New Store",
  "description": "A store for trendy clothing",
  "integration_type": "MANUAL",
  "product_count": 0,
  "is_active": true,
  "created_at": "2024-01-15T14:00:00Z"
}
```

### CSV Import

Import products from CSV file.

**Endpoint:** `POST /stores/{id}/csv-import/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/stores/1/csv-import/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "csv_file=@products.csv"
```

**CSV Format:**
```csv
title,product_url,image_url,price,tags
T-Shirt,https://example.com/tshirt,https://example.com/img.jpg,29.99,clothing
```

**Response:**
```json
{
  "message": "CSV import completed",
  "stats": {
    "created": 5,
    "updated": 0,
    "errors": 0
  }
}
```

### Shopify Sync

Sync products from Shopify.

**Endpoint:** `POST /stores/{id}/shopify-sync/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/stores/1/shopify-sync/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shopify_domain": "mystore.myshopify.com",
    "shopify_access_token": "shpat_xxxxx"
  }'
```

**Response:**
```json
{
  "message": "Shopify sync completed",
  "stats": {
    "created": 10,
    "updated": 5,
    "errors": 0
  }
}
```

## Products

### List Products

Get products, optionally filtered by store.

**Endpoint:** `GET /products/?store_id={store_id}`

**Request:**
```bash
curl http://localhost:8000/api/products/?store_id=1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Classic White T-Shirt",
      "handle": "white-tshirt",
      "product_url": "https://example.com/tshirt",
      "image_url": "https://example.com/tshirt.jpg",
      "price": "29.99",
      "vendor": "BrandName",
      "tags": "clothing,casual,tshirt",
      "tag_list": ["clothing", "casual", "tshirt"],
      "store": 1,
      "store_name": "Fashion Store",
      "is_active": true,
      "created_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

### Get Product

Get detailed product information.

**Endpoint:** `GET /products/{id}/`

**Request:**
```bash
curl http://localhost:8000/api/products/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## User Images

### Prepare Upload

Get a signed URL for uploading an image.

**Endpoint:** `POST /user-images/prepare-upload/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/user-images/prepare-upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "photo.jpg",
    "consent_given": true
  }'
```

**Response:**
```json
{
  "image_id": 42,
  "upload_url": "http://localhost:9000/wearlens/users/1/original/abc123.jpg?...",
  "upload_fields": {},
  "expires_in": 3600
}
```

### Upload Image

Upload the image to the signed URL (PUT request, not authenticated).

**Request:**
```bash
curl -X PUT "SIGNED_UPLOAD_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg
```

### Complete Upload

Notify the server that upload is complete and trigger processing.

**Endpoint:** `POST /user-images/{id}/complete/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/user-images/42/complete/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "success": true
  }'
```

**Response:**
```json
{
  "message": "Upload completed, processing started",
  "image": {
    "id": 42,
    "status": "PROCESSING",
    "consent_given": true,
    "created_at": "2024-01-15T15:00:00Z"
  }
}
```

### List User Images

Get all images for the current user.

**Endpoint:** `GET /user-images/`

**Request:**
```bash
curl http://localhost:8000/api/user-images/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 42,
      "user": 1,
      "original_path": "users/1/original/abc123.jpg",
      "processed_path": "users/1/processed/abc123.png",
      "processed_url": "http://localhost:9000/...",
      "processed_width": 1024,
      "processed_height": 1536,
      "status": "COMPLETED",
      "consent_given": true,
      "created_at": "2024-01-15T15:00:00Z",
      "processed_at": "2024-01-15T15:00:30Z"
    }
  ]
}
```

## Try-On Generation

### Create Generation

Start a new try-on generation.

**Endpoint:** `POST /tryon/`

**Rate Limit:** 10 requests per hour per user

**Request:**
```bash
curl -X POST http://localhost:8000/api/tryon/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_image_id": 42,
    "product_id": 1,
    "mask_type": "UPPER_BODY"
  }'
```

**Response:**
```json
{
  "message": "Generation queued successfully",
  "generation": {
    "id": 100,
    "user": 1,
    "user_image": 42,
    "product": 1,
    "product_title": "Classic White T-Shirt",
    "status": "QUEUED",
    "mask_type": "UPPER_BODY",
    "created_at": "2024-01-15T16:00:00Z"
  }
}
```

### List Generations

Get all generations for the current user.

**Endpoint:** `GET /generations/?status=SUCCEEDED`

**Request:**
```bash
curl http://localhost:8000/api/generations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 100,
      "user": 1,
      "user_image": 42,
      "product": 1,
      "product_title": "Classic White T-Shirt",
      "status": "SUCCEEDED",
      "output_url": "http://localhost:9000/...",
      "processing_time_seconds": 15.3,
      "created_at": "2024-01-15T16:00:00Z",
      "completed_at": "2024-01-15T16:00:15Z"
    }
  ]
}
```

### Get Generation

Get details of a specific generation.

**Endpoint:** `GET /generations/{id}/`

**Request:**
```bash
curl http://localhost:8000/api/generations/100/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 100,
  "user": 1,
  "user_image": 42,
  "product": 1,
  "product_title": "Classic White T-Shirt",
  "prompt": "Edit the first image (full-body person photo)...",
  "mask_type": "UPPER_BODY",
  "output_path": "generations/1/100/result.png",
  "output_url": "http://localhost:9000/...",
  "status": "SUCCEEDED",
  "error_message": "",
  "openai_request_id": "req_abc123",
  "openai_model": "gpt-image-1.5",
  "processing_time_seconds": 15.3,
  "created_at": "2024-01-15T16:00:00Z",
  "completed_at": "2024-01-15T16:00:15Z"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "User consent required. Please ensure consent_given=True on the user image."
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred"
}
```

## Postman Collection

Import this JSON to test the API in Postman:

```json
{
  "info": {
    "name": "WearLens API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/auth/register/",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"username\": \"testuser\",\n  \"password\": \"testpass123\",\n  \"password_confirm\": \"testpass123\",\n  \"role\": \"CUSTOMER\"\n}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/auth/login/",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"testpass123\"\n}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```
