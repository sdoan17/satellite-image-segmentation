# Satellite Segmentation Frontend

Next.js portfolio demo for issue U5. The app opens on curated sample artifacts and can optionally call the FastAPI inference backend for uploaded images.

## Local Development

```bash
pnpm install
pnpm sync:artifacts
pnpm dev
```

Open `http://localhost:3000`.

## Optional Inference API

Set `NEXT_PUBLIC_INFERENCE_API_URL` to the backend origin, without a trailing `/predict` path:

```bash
NEXT_PUBLIC_INFERENCE_API_URL=http://localhost:8000
```

When this variable is not set, curated samples and evaluation content still work and the upload panel explains that live inference is unavailable.

## Artifact Source

`scripts/sync-artifacts.mjs` copies generated evaluation artifacts from `../docs/evaluation` into `public/evaluation` so the frontend reads generated project data instead of hardcoded metrics or sample paths.

Current sample predictions and metrics reflect the generated artifact status. If those artifacts are placeholders or `not_run`, the UI labels them that way rather than presenting them as final model scores.

## Checks

```bash
pnpm test
pnpm build
```
