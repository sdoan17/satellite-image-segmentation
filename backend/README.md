# Satellite Segmentation Backend

FastAPI service for serving the trained PyTorch satellite segmentation model.

## API

- `GET /health` returns `200` when the model is loaded and `503` when model loading failed.
- `POST /predict` accepts one image upload as multipart form field `file`.
- Successful predictions return base64 PNG mask and overlay images, class metadata, original input dimensions, and a demo disclaimer.

Uploads must be image files and are rejected when they exceed `1,048,576` pixels. The backend rejects oversized inputs instead of resizing them so inference latency and memory use stay predictable.

## Local Startup

From the repository root:

```bash
python3 -m pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

The default model path is `models/pytorch_model.pth`. Override it when needed:

```bash
SATSEG_MODEL_PATH=/absolute/path/to/pytorch_model.pth uvicorn backend.app.main:app --port 8000
```

Allow specific frontend origins with a comma-separated list:

```bash
BACKEND_CORS_ORIGINS=https://example.vercel.app,http://localhost:3000 uvicorn backend.app.main:app --port 8000
```

Copy `backend/.env.example` for hosted configuration. The backend owns PyTorch model loading, image validation, CORS, `/health`, and `/predict`; it should run on a container or Python service with enough memory for PyTorch and `models/pytorch_model.pth`.

## Smoke Checks

```bash
curl -i http://localhost:8000/health
curl -i -X POST http://localhost:8000/predict \
  -F "file=@images/image1.jpg"
```

If model dependencies or the checkpoint are unavailable, `/health` returns `503` and `/predict` refuses inference requests.

## Docker

Build and run from the repository root:

```bash
docker build -f backend/Dockerfile -t satellite-segmentation-backend .
docker run --rm -p 8000:8000 satellite-segmentation-backend
```

For hosted deployments, allocate enough memory for PyTorch plus the `models/pytorch_model.pth` checkpoint. Keep the frontend on Vercel and point it at this backend URL.
