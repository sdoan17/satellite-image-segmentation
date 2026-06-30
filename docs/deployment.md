# Deployment

This project is split into two deployable surfaces:

- `frontend/`: the Next.js case-study and demo UI, intended for Vercel.
- `backend/`: the FastAPI inference API, intended for a container or Python runtime that can load PyTorch and `models/pytorch_model.pth`.

Do not host PyTorch inference inside Vercel for this v1 architecture. The frontend remains useful without live inference because curated samples, metrics, class legend, and case-study content are bundled as static artifacts.

## Frontend Hosting

Deploy `frontend/` as the Vercel project root when possible. `frontend/vercel.json` contains the direct frontend build settings:

```bash
pnpm install --frozen-lockfile
pnpm build
```

The repository root also has `vercel.json` for monorepo-style deployments where Vercel is connected to the repository root and builds the frontend with `pnpm --dir frontend build`.

Set this environment variable in Vercel only when a backend is deployed:

| Variable | Required | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_INFERENCE_API_URL` | No | Base URL for the FastAPI backend, for example `https://satseg-api.example.com`. Leave blank to disable live upload inference. |

When `NEXT_PUBLIC_INFERENCE_API_URL` is blank, uploads are disabled and the UI keeps curated samples available. When it is set, the frontend checks `${NEXT_PUBLIC_INFERENCE_API_URL}/health` and sends uploads to `${NEXT_PUBLIC_INFERENCE_API_URL}/predict`.

## Backend Hosting

Deploy the backend on a service that supports a Python web process, PyTorch dependencies, the model checkpoint, predictable memory, startup health checks, and restarts. Container hosts such as Render, Fly.io, Railway, Google Cloud Run, AWS ECS, or a VM are better fits than Vercel serverless functions for this model-serving path.

Required backend runtime variables are documented in `backend/.env.example`:

| Variable | Required | Purpose |
| --- | --- | --- |
| `SATSEG_MODEL_PATH` | No | Path to the checkpoint. Defaults to `models/pytorch_model.pth` from the repository root. |
| `BACKEND_CORS_ORIGINS` | Yes for hosted frontend | Comma-separated origins allowed to call the API, for example `https://your-project.vercel.app,http://localhost:3000`. |

The Docker entrypoint runs:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Health And CORS

The backend exposes:

- `GET /health`: returns `200` with `{"status":"healthy","model_loaded":true}` when the checkpoint is loaded.
- `GET /health`: returns `503` with `{"status":"unhealthy","model_loaded":false,"error":"..."}` when startup cannot load the model.
- `POST /predict`: accepts multipart form field `file` and returns base64 PNG prediction imagery.

CORS is enforced by `BACKEND_CORS_ORIGINS`. Include every frontend origin that should call the API: local development, Vercel preview URLs if needed, and the production Vercel URL.

If `/health` is down or the model is not loaded, the frontend surfaces an unavailable upload state and leaves curated samples and case-study content usable.

## Smoke Checks

Frontend without backend:

```bash
cd frontend
cp .env.example .env.local
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://localhost:3000`. The curated samples should render and the upload control should explain that live inference is not configured.

Backend local:

```bash
python3 -m pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
curl -i http://localhost:8000/health
curl -i -X POST http://localhost:8000/predict -F "file=@images/image1.jpg"
```

Frontend with backend:

```bash
cd frontend
NEXT_PUBLIC_INFERENCE_API_URL=http://localhost:8000 pnpm dev
```

Open `http://localhost:3000`, upload `images/image1.jpg`, and confirm the request goes to `http://localhost:8000/predict`.

Hosted smoke checks:

```bash
curl -i https://your-backend.example.com/health
curl -i -X POST https://your-backend.example.com/predict -F "file=@images/image1.jpg"
```

Then open the Vercel URL with `NEXT_PUBLIC_INFERENCE_API_URL` set to the backend origin and confirm uploads either return a model prediction or show the documented unavailable state while curated samples remain visible.
