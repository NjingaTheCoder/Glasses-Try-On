# Glasses Try-On

Virtual glasses try-on web app — upload a face photo and overlay glasses using MediaPipe Face Mesh entirely in the browser.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, React Router v6 |
| State | Zustand |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2 |
| Database | PostgreSQL 16 |
| Storage | Firebase Storage |
| Face Detection | MediaPipe Face Mesh (WASM, runs 100% client-side) |
| Rendering | HTML5 Canvas (instant preview) + OpenAI gpt-image-1 (AI render) |
| Auth | Firebase Auth (email/password, admin only) |

## Monorepo Structure

```
glasses-tryon/
├── frontend/          React + Vite app
├── backend/           FastAPI app
├── docker-compose.yml Local Postgres + backend
└── README.md
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker + Docker Compose
- A Firebase project (free Spark plan is enough)

---

## Firebase Setup

### 1. Create project and enable services

1. Go to [Firebase Console](https://console.firebase.google.com) → New project.
2. **Authentication** → Sign-in method → Enable **Email/Password**.
3. **Authentication** → Users → Add user (this is your admin account).
4. **Storage** → Get started (choose your region).

### 2. Firebase Storage CORS configuration

The canvas reads glasses images with `crossOrigin="anonymous"`. Firebase Storage requires explicit CORS headers.

Create `cors.json`:

```json
[
  {
    "origin": ["http://localhost:5173", "https://yourdomain.com"],
    "method": ["GET"],
    "maxAgeSeconds": 3600
  }
]
```

Apply it (requires [gsutil](https://cloud.google.com/storage/docs/gsutil_install)):

```bash
gsutil cors set cors.json gs://your-project.appspot.com
```

### 3. Firebase Storage security rules

In Firebase Console → Storage → Rules, paste:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Glasses PNGs: only admins can write, anyone can read
    match /glasses/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    // Face photos: anyone can write (session upload), only auth reads
    match /faces/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if true;
    }
  }
}
```

### 4. Service account (for backend token verification)

1. Firebase Console → Project Settings → Service Accounts → **Generate new private key**.
2. Base64-encode it:
   ```bash
   # macOS / Linux
   base64 -i serviceAccount.json | tr -d '\n'
   # Windows PowerShell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("serviceAccount.json"))
   ```
3. Paste the result into `backend/.env` as `FIREBASE_SERVICE_ACCOUNT_BASE64`.

### 5. Web app config (for frontend)

Firebase Console → Project Settings → Your apps → Add web app → copy the config object keys into `frontend/.env`.

---

## Local Development

### Start PostgreSQL (Docker)

```bash
docker compose up db -d
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — fill in FIREBASE_SERVICE_ACCOUNT_BASE64 if using admin features
# Edit .env — fill in OPENAI_API_KEY to enable the AI realistic render feature

# Run migrations
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/glasses_tryon \
  alembic upgrade head

# Seed 7 sample products
python scripts/seed.py

# Start dev server
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env — fill in all VITE_FIREBASE_* values

npm run dev
```

App: http://localhost:5173

> **MediaPipe WASM note**: On first `npm run dev`, `vite-plugin-static-copy` copies the MediaPipe WASM/BIN assets from `node_modules/@mediapipe/face_mesh/` into the dev server's virtual `/mediapipe/` path. If face detection 404s on `.wasm` files, restart the dev server once and hard-refresh.

### Run everything with Docker Compose

```bash
docker compose up --build
```

Then run migrations inside the container:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed.py
```

---

## Environment Variables

### `frontend/.env`

| Variable | Description |
|---|---|
| `VITE_FIREBASE_API_KEY` | Firebase web API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | e.g. `yourproject.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | e.g. `yourproject.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase sender ID |
| `VITE_FIREBASE_APP_ID` | Firebase app ID |
| `VITE_API_BASE_URL` | Backend URL (default `http://localhost:8000`) |

### `backend/.env`

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL async URL, e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/glasses_tryon` |
| `FIREBASE_SERVICE_ACCOUNT_BASE64` | Base64-encoded Firebase service account JSON |
| `CORS_ORIGINS` | JSON array of allowed origins, e.g. `["http://localhost:5173"]` |
| `OPENAI_API_KEY` | OpenAI API key — required for the AI realistic render feature |
| `OPENAI_IMAGE_MODEL` | OpenAI image model (default: `gpt-image-1`) |

---

## API Routes

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | — | Health check |
| GET | `/api/products` | — | List products (filterable) |
| GET | `/api/products/:id` | — | Get product |
| POST | `/api/products` | Admin | Create product |
| PUT | `/api/products/:id` | Admin | Update product |
| DELETE | `/api/products/:id` | Admin | Delete product |
| POST | `/api/upload/face` | — | Record face upload metadata |
| POST | `/api/try-on/render-ai` | — | Generate AI realistic render via OpenAI |

`POST /api/try-on/render-ai` accepts `multipart/form-data`:

| Field | Type | Required | Description |
|---|---|---|---|
| `face_image` | File | Yes | The user's face photo (JPEG/PNG ≤ 10 MB) |
| `glasses_url` | string | Yes | HTTPS URL of the glasses product image |
| `guide_image` | File | No | Current canvas preview exported as PNG (positional hint for the AI) |

Returns `{ "image_url": "data:image/png;base64,..." }`.

Query params for `GET /api/products`: `shape`, `color`, `min_price`, `max_price`, `q`, `skip`, `limit`

---

## Frontend Routes

| Path | Description |
|---|---|
| `/` | Public product catalog |
| `/product/:id` | Product detail with Try On CTA |
| `/try-on` | Upload face photo + try-on |
| `/try-on/:productId` | Try-on with a preselected product |
| `/admin/login` | Firebase email/password login |
| `/admin` | Admin product dashboard |
| `/admin/products/new` | Create product + anchor editor |
| `/admin/products/:id/edit` | Edit product + anchor editor |

---

## Admin Workflow

1. Log in at `/admin/login` with your Firebase user.
2. From the dashboard, click **+ Add Product**.
3. Fill in name, brand, price, shape, color.
4. Upload a **transparent PNG** of the glasses.
5. The **Anchor Point Editor** appears — click to place:
   - **Bridge Center** (blue) — center of the nose bridge
   - **Left Temple End** (red) — far left tip of the frame
   - **Right Temple End** (green) — far right tip of the frame
6. All three anchors are required before saving.

---

## Try-On Flow

1. Go to `/try-on` (or click **Try On** on any product card).
2. Drag-and-drop or choose a front-facing face photo (JPG/PNG ≤ 10 MB).
3. MediaPipe Face Mesh runs entirely in the browser — no photo is sent to any server.
4. Once landmarks are detected, select glasses from the sidebar (desktop) or strip (mobile).
5. The canvas updates instantly — no re-detection when switching glasses.
6. Use **Download** to save the canvas preview as PNG, or **Share** to use the Web Share API.

If no face is found: *"We couldn't find a face. Try a clearer front-facing photo."*

### AI Realistic Render

After the instant canvas preview appears:

7. Click **✨ Generate realistic render** — the face photo and glasses image are sent to the backend, which calls the OpenAI image edit API.
8. Generation takes roughly 15–30 seconds. The button shows a spinner while waiting; the instant preview remains usable.
9. The AI-rendered image appears below the canvas with a **⬇ Download render** button.
10. If the request fails, an error message is shown with a **Retry** link.

> **Requires** `OPENAI_API_KEY` in `backend/.env`. The feature is silently hidden when no product or face file is present. Photos are never stored — they exist only for the duration of the API call.

---

## Overlay Math

```
lm33  = right eye outer landmark  (landmark index 33)
lm263 = left eye outer landmark   (landmark index 263)
lm168 = nose bridge top           (landmark index 168)

eye_distance  = √((lm263.x − lm33.x)² + (lm263.y − lm33.y)²)
tilt_angle    = atan2(lm263.y − lm33.y,  lm263.x − lm33.x)
glasses_width = eye_distance × 2.2

canvas.translate(lm168.x, lm168.y)
canvas.rotate(tilt_angle)
canvas.drawImage(glassesImg,
  −bridge_x × glasses_width,
  −bridge_y × glasses_height,
  glasses_width, glasses_height)
```

Anchor values (`bridge_x`, `bridge_y`, etc.) are stored normalized 0–1 relative to the glasses image dimensions.

---

## Alembic Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after changing models
alembic revision --autogenerate -m "your description"

# Roll back one step
alembic downgrade -1
```
