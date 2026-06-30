# Satellite Image Semantic Segmentation Demo

Portfolio-ready semantic segmentation demo for satellite-style imagery. The project pairs a PyTorch model workflow with generated evaluation artifacts, a FastAPI inference service, and a Next.js case-study frontend so reviewers can inspect predictions without opening the training notebook first.

The demo is built for learning, portfolio review, and reproducible experimentation. It is not an authoritative geospatial analysis tool, a GIS replacement, or a production remote-sensing system. Predictions should be treated as model outputs that need human review and dataset-specific validation.

## Demo Surface

The frontend lives in [`frontend/`](frontend/) and can run in two modes:

- Static case study mode: reads curated artifacts from [`docs/evaluation/`](docs/evaluation/) and remains usable without a live model server.
- Live inference mode: calls the FastAPI backend when `NEXT_PUBLIC_INFERENCE_API_URL` points to a deployed or local API.

Current sample artifacts:

| Sample | Original | Prediction | Overlay | Source |
| --- | --- | --- | --- | --- |
| image1 | [`docs/evaluation/samples/01-image1-original.jpg`](docs/evaluation/samples/01-image1-original.jpg) | [`docs/evaluation/samples/01-image1-prediction.png`](docs/evaluation/samples/01-image1-prediction.png) | [`docs/evaluation/samples/01-image1-overlay.png`](docs/evaluation/samples/01-image1-overlay.png) | [`docs/evaluation/samples/metadata.json`](docs/evaluation/samples/metadata.json) |
| image2 | [`docs/evaluation/samples/02-image2-original.jpg`](docs/evaluation/samples/02-image2-original.jpg) | [`docs/evaluation/samples/02-image2-prediction.png`](docs/evaluation/samples/02-image2-prediction.png) | [`docs/evaluation/samples/02-image2-overlay.png`](docs/evaluation/samples/02-image2-overlay.png) | [`docs/evaluation/samples/metadata.json`](docs/evaluation/samples/metadata.json) |

The checked-in sample predictions are currently marked as `generated_placeholder` in [`docs/evaluation/samples/metadata.json`](docs/evaluation/samples/metadata.json). Regenerate them with the PyTorch runtime and local Dubai dataset before using them as model-backed performance evidence.

## Repository Map

| Path | Purpose |
| --- | --- |
| [`notebook/segmentation_pytorch.ipynb`](notebook/segmentation_pytorch.ipynb) | Primary PyTorch training and evaluation notebook. |
| [`notebook/segmentation.ipynb`](notebook/segmentation.ipynb) | Earlier segmentation exploration notebook. |
| [`models/pytorch_model.pth`](models/pytorch_model.pth) | Selected checkpoint used by evaluation scripts and the backend by default. |
| [`src/satseg/`](src/satseg/) | Importable model, inference, metrics, constants, and visualization code extracted from notebook assumptions. |
| [`scripts/evaluate_model.py`](scripts/evaluate_model.py) | Generates validation/test metrics into `docs/evaluation/metrics.json`. |
| [`scripts/generate_demo_artifacts.py`](scripts/generate_demo_artifacts.py) | Generates sample originals, predictions, overlays, and metadata for the demo. |
| [`docs/evaluation/metrics.json`](docs/evaluation/metrics.json) | Machine-readable source of truth for aggregate and per-class evaluation results. |
| [`docs/evaluation/classes.json`](docs/evaluation/classes.json) | Class names, colors, and ignored label metadata. |
| [`backend/`](backend/) | FastAPI service for model loading, image validation, health checks, and prediction responses. |
| [`frontend/`](frontend/) | Next.js demo and case-study UI designed for Vercel hosting. |
| [`docs/deployment.md`](docs/deployment.md) | Deployment boundaries for Vercel frontend hosting and separate PyTorch backend serving. |

## Model And Data Contract

The primary model path is [`models/pytorch_model.pth`](models/pytorch_model.pth). The class contract comes from [`docs/evaluation/classes.json`](docs/evaluation/classes.json) and the primary notebook:

| ID | Class | RGB | Used in metrics |
| --- | --- | --- | --- |
| 0 | building | `[60, 16, 152]` | yes |
| 1 | land | `[132, 41, 246]` | yes |
| 2 | road | `[110, 193, 228]` | yes |
| 3 | vegetation | `[254, 221, 58]` | yes |
| 4 | water | `[226, 169, 41]` | yes |
| 5 | unlabeled | `[155, 155, 155]` | ignored label |

The local Dubai satellite dataset is expected at `DubaiDataset/`. That directory is intentionally ignored because it is a local data artifact rather than source code. The repository keeps class metadata separately so scripts, docs, backend, and frontend do not depend on ignored dataset files.

## Evaluation Status

Evaluation claims in this README should be updated from [`docs/evaluation/metrics.json`](docs/evaluation/metrics.json), not typed by hand.

Current generated artifact status:

| Split | Status | Pixel accuracy | Mean IoU | Reason |
| --- | --- | --- | --- | --- |
| validation | `not_run` | `null` | `null` | Local `DubaiDataset` labels and the PyTorch runtime were not available in this clone. |
| test | `not_run` | `null` | `null` | Local `DubaiDataset` labels and the PyTorch runtime were not available in this clone. |

Per-class IoU matters because segmentation quality is not evenly distributed across classes. Pixel accuracy can look strong when large background or majority classes dominate the image, while roads, water, or smaller building regions may still be poorly segmented. IoU exposes the overlap quality for each class and prevents a high aggregate score from hiding weak minority-class behavior.

The current `not_run` metrics mean this repository has the evaluation pipeline and artifact shape in place, but this checkout does not yet contain verified validation/test scores. Regenerate metrics with the local dataset before making performance claims.

## Local Setup

Use Python 3.9 or newer. Commands are intended to run from the repository root unless noted otherwise.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Optional frontend dependencies are installed from the frontend workspace:

```bash
cd frontend
pnpm install
```

## Regenerate Evaluation Artifacts

The scripts can emit placeholder artifacts when the full dataset or PyTorch runtime is unavailable, but model-backed metrics require the local dataset and dependencies.

```bash
python3 scripts/evaluate_model.py
python3 scripts/generate_demo_artifacts.py
```

After regeneration, review:

- [`docs/evaluation/metrics.json`](docs/evaluation/metrics.json) for validation/test status, pixel accuracy, mean IoU, per-class IoU, class distribution, and generation timestamp.
- [`docs/evaluation/samples/metadata.json`](docs/evaluation/samples/metadata.json) for whether sample predictions are model-backed or placeholders.
- [`docs/evaluation/samples/`](docs/evaluation/samples/) for original, prediction, and overlay images consumed by the frontend.

To sync regenerated artifacts into the Next.js public directory:

```bash
cd frontend
pnpm sync:artifacts
```

## Run The Backend

The backend owns PyTorch model loading, file validation, CORS, health checks, and prediction responses. It defaults to [`models/pytorch_model.pth`](models/pytorch_model.pth).

```bash
python3 -m pip install -r requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Smoke check:

```bash
curl -i http://localhost:8000/health
curl -i -X POST http://localhost:8000/predict -F "file=@images/image1.jpg"
```

Useful environment variables:

| Variable | Required | Purpose |
| --- | --- | --- |
| `SATSEG_MODEL_PATH` | No | Override the model checkpoint path. |
| `BACKEND_CORS_ORIGINS` | Yes for hosted frontend | Comma-separated frontend origins allowed to call the API. |

See [`backend/README.md`](backend/README.md) for API details, upload limits, Docker usage, and hosted backend notes.

## Run The Frontend

```bash
cd frontend
pnpm install
pnpm sync:artifacts
pnpm dev
```

Open `http://localhost:3000`.

Without `NEXT_PUBLIC_INFERENCE_API_URL`, the upload path is disabled and curated samples still render. To connect local live inference:

```bash
cd frontend
NEXT_PUBLIC_INFERENCE_API_URL=http://localhost:8000 pnpm dev
```

See [`frontend/README.md`](frontend/README.md) for frontend-specific checks and artifact sync details.

## Deployment Boundaries

Use Vercel for the user-facing Next.js frontend and a separate Python/container service for PyTorch inference. Do not put the v1 PyTorch model-serving path inside Vercel serverless functions; PyTorch dependencies and the checkpoint are better suited to a backend host with predictable memory and startup behavior.

Recommended split:

- Frontend: deploy [`frontend/`](frontend/) to Vercel. It works with static generated artifacts even when no backend URL is configured.
- Backend: deploy [`backend/`](backend/) to a container or Python runtime such as Render, Fly.io, Railway, Google Cloud Run, AWS ECS, or a VM.
- Configuration: set `NEXT_PUBLIC_INFERENCE_API_URL` in the frontend only after the backend is deployed and healthy.

See [`docs/deployment.md`](docs/deployment.md) for environment variables, health checks, CORS expectations, and smoke checks.

## Verification Commands

Run the focused checks for the surfaces you change:

```bash
pytest
cd frontend && pnpm test && pnpm build
```

For README-only changes, also verify links and claims against the generated artifacts:

```bash
python3 -m json.tool docs/evaluation/metrics.json >/dev/null
python3 -m json.tool docs/evaluation/classes.json >/dev/null
python3 -m json.tool docs/evaluation/samples/metadata.json >/dev/null
```

## Limitations

- Current checked-in validation/test metrics are `not_run`, so the README and frontend must not claim measured model performance until metrics are regenerated with the local dataset and runtime.
- Current checked-in demo predictions are placeholders, not confirmed model-backed outputs.
- The backend accepts satellite-style image uploads for demonstration, but the model is only as reliable as its training data, preprocessing assumptions, and evaluation coverage.
- This project does not perform production GIS validation, coordinate-aware analysis, sensor calibration, or real-world change detection.
- Large model artifacts can make cloning and hosting heavier. Keep [`models/pytorch_model.pth`](models/pytorch_model.pth) as the intentional checkpoint unless a replacement policy is documented.

## Project Direction

The broader implementation plan is tracked in [`docs/plans/2026-06-23-001-feat-satellite-demo-deployment-plan.md`](docs/plans/2026-06-23-001-feat-satellite-demo-deployment-plan.md). The v1 direction is a public portfolio project that keeps the ML evidence, inference API, frontend demo, and deployment boundaries aligned without overstating model authority.
