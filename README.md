# WearLens - Virtual Try-On SaaS Platform

A production-quality virtual try-on platform that allows clothing merchants to offer AI-powered try-on experiences to their customers. Built with React, Django, and OpenAI's image generation API.

## Features

- **Multi-tenant Architecture**: Support for multiple merchants and stores
- **Store Integrations**: Shopify OAuth (scaffolded) + CSV product import
- **AI-Powered Try-On**: Photorealistic garment visualization using OpenAI GPT Image models
- **Async Processing**: Celery-based background jobs for image processing and generation
- **Secure Storage**: S3-compatible object storage (MinIO) with signed URLs
- **Role-Based Access**: Merchant and Customer roles with proper permissions
- **Scalable**: Production-ready with Docker containerization

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Query (server state)
- React Router (routing)

### Backend
- Django 5.0 + Django REST Framework
- PostgreSQL (database)
- Celery + Redis (async jobs)
- MinIO (S3-compatible storage)
- OpenAI API (image generation)

### Infrastructure
- Docker + Docker Compose
- Nginx (production reverse proxy - optional)

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- OpenAI API key (get one at https://platform.openai.com)
- Node.js 18+ (for local frontend development without Docker)
- Python 3.11+ (for local backend development without Docker)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd WearLens
```

### 2. Configure Environment Variables

Copy the example environment files and configure them:

```bash
# Infrastructure (Docker Compose)
cp infra/.env.example infra/.env

# Backend API
cp apps/api/.env.example apps/api/.env

# Frontend
cp apps/web/.env.example apps/web/.env
```

**IMPORTANT**: Edit `infra/.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. Start All Services

```bash
# Using Make (recommended)
make up

# Or using Docker Compose directly
docker compose up --build
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (port 9000, console: 9001)
- Django API (port 8000)
- Celery Worker
- React Frontend (port 5173)

### 4. Run Database Migrations

In a new terminal:

```bash
make migrate

# Or manually
docker compose exec api python manage.py migrate
```

### 5. Create a Superuser

```bash
make createsuperuser

# Or manually
docker compose exec api python manage.py createsuperuser
```

### 6. Seed Sample Data (Optional)

```bash
make seed

# Or manually
docker compose exec api python /app/scripts/seed.py
```

### 7. Access the Application

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **MinIO Console**: http://localhost:9001 (user: minioadmin, pass: minioadmin)

## Common Commands (Makefile)

```bash
make up              # Start all services
make down            # Stop all services
make build           # Rebuild containers
make logs            # View all logs
make logs-api        # View API logs
make logs-celery     # View Celery worker logs
make logs-web        # View frontend logs
make shell           # Django shell
make migrate         # Run migrations
make makemigrations  # Create new migrations
make createsuperuser # Create Django superuser
make seed            # Seed sample data
make test            # Run all tests
make test-api        # Run backend tests
make test-web        # Run frontend tests
make lint            # Lint all code
make format          # Format all code
make clean           # Clean up containers and volumes
```

## Development Workflow

### Backend Development

1. **Make model changes** in `apps/api/apps/<app_name>/models.py`
2. **Create migrations**:
   ```bash
   make makemigrations
   ```
3. **Apply migrations**:
   ```bash
   make migrate
   ```
4. **Run tests**:
   ```bash
   make test-api
   ```

### Frontend Development

1. **Install dependencies** (if not using Docker):
   ```bash
   cd apps/web
   npm install
   ```
2. **Run dev server**:
   ```bash
   npm run dev
   ```
3. **Build for production**:
   ```bash
   npm run build
   ```

### Adding New Celery Tasks

1. Define task in `apps/api/apps/<app_name>/tasks.py`
2. Import task in `config/celery.py` if needed
3. Restart celery worker:
   ```bash
   docker compose restart celery
   ```

## API Documentation

See [docs/api_examples.md](docs/api_examples.md) for detailed API usage examples.

### Key Endpoints

- `POST /api/auth/login/` - Login
- `POST /api/auth/register/` - Register
- `GET /api/stores/` - List stores
- `POST /api/stores/{id}/csv-import/` - Import products via CSV
- `POST /api/user-images/prepare-upload/` - Get signed upload URL
- `POST /api/tryon/` - Create try-on generation
- `GET /api/generations/{id}/` - Get generation status

## Architecture

See [docs/architecture.md](docs/architecture.md) for system design and data flow.

### Key Components

1. **Authentication**: Token-based auth with user roles
2. **Stores**: Multi-tenant store management
3. **Products**: Product catalog with variant support
4. **Images**: User photo uploads with processing pipeline
5. **Try-On**: AI generation with Celery async processing
6. **Storage**: MinIO S3-compatible storage with signed URLs

## Environment Variables

### Infrastructure (infra/.env)

```env
OPENAI_API_KEY=sk-proj-xxx              # Required: Your OpenAI API key
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: OpenAI API base URL
POSTGRES_DB=wearlens
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

### Backend (apps/api/.env)

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@db:5432/wearlens
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=wearlens
ALLOWED_HOSTS=localhost,127.0.0.1,api
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (apps/web/.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Testing

### Run All Tests

```bash
make test
```

### Backend Tests Only

```bash
make test-api

# Or with coverage
docker compose exec api pytest --cov=apps --cov-report=html
```

### Frontend Tests Only

```bash
make test-web

# Or locally
cd apps/web
npm test
```

## Deployment

### Production Considerations

1. **Environment Variables**:
   - Use strong `SECRET_KEY`
   - Set `DEBUG=False`
   - Configure proper `ALLOWED_HOSTS`
   - Use production-grade passwords

2. **Database**:
   - Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
   - Enable backups
   - Set up connection pooling

3. **Storage**:
   - Use AWS S3 or Google Cloud Storage instead of MinIO
   - Configure CDN for static assets

4. **Celery**:
   - Use managed Redis (AWS ElastiCache, Redis Cloud)
   - Monitor queue sizes
   - Set up auto-scaling for workers

5. **Security**:
   - Enable HTTPS
   - Configure CORS properly
   - Set up rate limiting
   - Enable security headers

### Docker Production Build

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Deploy to your infrastructure
# (AWS ECS, Google Cloud Run, Kubernetes, etc.)
```

## Troubleshooting

### Services won't start

```bash
# Clean up and restart
make clean
make up
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker compose ps

# View database logs
docker compose logs db
```

### Celery tasks not processing

```bash
# Check Celery worker logs
make logs-celery

# Restart Celery
docker compose restart celery
```

### Image uploads failing

```bash
# Check MinIO is running
docker compose ps minio

# Access MinIO console at http://localhost:9001
# Verify bucket exists
```

### OpenAI API errors

- Verify your API key is correct in `infra/.env`
- Check your OpenAI account has credits
- View detailed errors in Celery logs: `make logs-celery`

## Project Structure

```
WearLens/
├── apps/
│   ├── api/          # Django backend
│   │   ├── apps/     # Django apps
│   │   └── config/   # Django settings
│   └── web/          # React frontend
│       └── src/      # React source code
├── infra/            # Infrastructure configs
├── scripts/          # Utility scripts
└── docs/             # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: <repository-issues-url>
- Documentation: [docs/](docs/)

## Roadmap

- [ ] Shopify OAuth complete implementation
- [ ] Advanced segmentation models (SAM, U-Net)
- [ ] Multi-angle try-on (front, side, back)
- [ ] Video try-on support
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] A/B testing framework
- [ ] Multi-language support
