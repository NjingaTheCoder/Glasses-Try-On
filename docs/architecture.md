# WearLens Architecture

## System Overview

WearLens is a multi-tenant SaaS platform that enables clothing merchants to offer AI-powered virtual try-on experiences to their customers. The system uses OpenAI's image generation API to create photorealistic try-on images.

## Architecture Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   React     │◄────►│   Django    │◄────►│  PostgreSQL │
│  Frontend   │      │   REST API  │      │  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                     ┌──────┴──────┐
                     ▼             ▼
              ┌─────────┐    ┌─────────┐
              │  Celery │    │  MinIO  │
              │ Workers │    │   S3    │
              └─────────┘    └─────────┘
                     │
                     ▼
              ┌──────────────┐
              │   OpenAI     │
              │     API      │
              └──────────────┘
```

## Core Components

### 1. Frontend (React + TypeScript)

**Technology Stack:**
- React 18 with TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Query (server state management)
- React Router (routing)
- Axios (HTTP client)

**Key Features:**
- Authentication with JWT tokens
- Store and product management
- Photo upload with consent handling
- Real-time generation status updates
- Result gallery with auto-refresh

**Pages:**
- `/login` - Authentication
- `/dashboard` - Store management
- `/store/:id/products` - Product browsing and import
- `/tryon` - Virtual try-on interface

### 2. Backend (Django + DRF)

**Technology Stack:**
- Django 5.0
- Django REST Framework
- PostgreSQL (database)
- Celery + Redis (async tasks)
- MinIO (S3-compatible storage)
- OpenAI Python SDK

**Apps Structure:**

#### authentication
- Custom User model with role-based access (MERCHANT, CUSTOMER, ADMIN)
- JWT-based authentication
- Token refresh mechanism

#### stores
- Multi-tenant store management
- Shopify OAuth integration (scaffolded)
- CSV product import
- Store API key management

#### products
- Product catalog with variants
- Image caching
- Tag-based filtering
- Store-scoped queries

#### images
- User photo upload with signed URLs
- EXIF orientation normalization
- Image resizing and optimization
- Consent tracking
- Processing status management

#### tryon
- Generation request handling
- Prompt building with templates
- OpenAI API integration
- Result storage and retrieval
- Session grouping

#### webhooks
- Shopify webhook handlers (scaffolded)
- Webhook verification
- Product sync automation

### 3. Storage Layer (MinIO)

**Purpose:**
- Private object storage for sensitive images
- S3-compatible API
- Signed URL generation for secure access

**Storage Structure:**
```
/wearlens/
  ├── users/{user_id}/
  │   ├── original/{image_id}.jpg
  │   └── processed/{image_id}.png
  ├── products/{product_id}/
  │   └── {image_id}.jpg
  └── generations/{user_id}/{generation_id}/
      └── result.png
```

### 4. Async Processing (Celery)

**Tasks:**

1. **process_user_image**
   - Normalize EXIF orientation
   - Resize to max 1536px
   - Convert to PNG/JPEG
   - Update metadata

2. **fetch_and_cache_product_image**
   - Download product image
   - Process and optimize
   - Cache in MinIO

3. **run_tryon_generation**
   - Load user and product images
   - Build prompt
   - Call OpenAI API with retries
   - Store result in MinIO
   - Update generation status

**Configuration:**
- Broker: Redis
- Result backend: Redis
- Max retries: 3
- Task timeout: 30 minutes

## Data Flow

### Try-On Generation Flow

1. **User uploads photo:**
   ```
   Frontend → API: POST /api/user-images/prepare-upload/
   API → MinIO: Generate signed upload URL
   API → Frontend: Return signed URL
   Frontend → MinIO: Upload image directly
   Frontend → API: POST /api/user-images/{id}/complete/
   API → Celery: Trigger process_user_image task
   ```

2. **User selects product and creates generation:**
   ```
   Frontend → API: POST /api/tryon/
   API: Validate consent & image status
   API: Build prompt from product details
   API: Create Generation record (QUEUED)
   API → Celery: Trigger run_tryon_generation task
   API → Frontend: Return generation ID
   ```

3. **Celery processes generation:**
   ```
   Celery: Update status to PROCESSING
   Celery → MinIO: Get signed URLs for images
   Celery → OpenAI: Call image edit API
   OpenAI → Celery: Return generated image
   Celery → MinIO: Upload result image
   Celery: Update Generation record (SUCCEEDED)
   ```

4. **Frontend polls for results:**
   ```
   Frontend → API: GET /api/generations/ (every 5s)
   API → Frontend: Return updated status
   Frontend: Display result when SUCCEEDED
   ```

## Security Architecture

### Authentication & Authorization

**JWT Tokens:**
- Access token: 1 hour lifetime
- Refresh token: 7 days lifetime
- Token rotation on refresh
- Blacklist support (optional)

**Permission Model:**
- Merchants can only access their own stores and products
- Customers can only access their own images and generations
- Admin has full access

### Data Privacy

**User Images:**
- Consent required before processing
- Stored in private buckets
- Accessed via signed URLs (1 hour expiration)
- Not shared with third parties

**API Keys:**
- OpenAI API key stored in environment variables
- Never logged or returned in API responses
- Separate model for store API keys

**Rate Limiting:**
- Try-on generation: 10 requests/hour per user
- General API: 1000 requests/hour per user
- Anonymous: 100 requests/hour per IP

## Scalability Considerations

### Horizontal Scaling

**Frontend:**
- Stateless React app
- Can run multiple instances behind load balancer
- CDN for static assets

**Backend:**
- Stateless Django API
- Multiple API instances with shared database
- Session data in JWT tokens (no server-side sessions)

**Celery:**
- Multiple worker instances
- Auto-scaling based on queue depth
- Task distribution via Redis

### Performance Optimization

**Database:**
- Indexed foreign keys
- Composite indexes for common queries
- Connection pooling
- Read replicas for analytics

**Caching:**
- Product images cached in MinIO
- API responses cached in Redis (future)
- Static files served via CDN (future)

**Image Processing:**
- Resize before uploading to OpenAI
- Lazy loading in frontend
- Thumbnail generation (future)

## Monitoring & Observability

**Logging:**
- Structured logging in JSON format
- Log levels: DEBUG (dev), INFO (prod)
- Sensitive data (images, keys) never logged

**Metrics (Future):**
- Request latency
- Generation success/failure rates
- Queue depths
- Storage usage
- API costs

**Error Tracking:**
- Exception logging in Celery tasks
- Error messages stored in Generation records
- Failed tasks can be retried manually

## Deployment Architecture

### Development (Docker Compose)

All services run on single host:
- 1 PostgreSQL container
- 1 Redis container
- 1 MinIO container
- 1 Django API container
- 1 Celery worker container
- 1 React dev server container

### Production (Recommended)

**Managed Services:**
- Database: AWS RDS or Google Cloud SQL
- Redis: AWS ElastiCache or Redis Cloud
- Storage: AWS S3 or Google Cloud Storage
- Container orchestration: ECS, Cloud Run, or Kubernetes

**Auto-scaling:**
- API: Scale based on CPU/memory
- Celery: Scale based on queue depth
- Database: Read replicas for heavy queries

## Future Enhancements

1. **Advanced Segmentation:**
   - Replace simple masks with SAM or U-Net
   - Support for different garment types
   - Better occlusion handling

2. **Multi-Angle Try-On:**
   - Front, side, and back views
   - 360-degree visualization

3. **Video Try-On:**
   - Animated try-on results
   - Real-time preview

4. **Analytics Dashboard:**
   - Conversion tracking
   - Popular products
   - Try-on success rates

5. **Mobile App:**
   - React Native app
   - Camera integration
   - Push notifications

6. **Shopify App:**
   - Complete OAuth flow
   - Embedded app experience
   - Automatic product sync
