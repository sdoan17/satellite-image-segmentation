# Satellite Image Semantic Segmentation

This repository contains a PyTorch semantic segmentation workflow for satellite imagery. The current baseline is notebook-centered, with a trained model checkpoint and planning docs for turning the work into a portfolio-ready demo.

## Current Repository

- `notebook/segmentation_pytorch.ipynb` is the primary PyTorch training and evaluation notebook.
- `notebook/segmentation.ipynb` contains the earlier segmentation exploration workflow.
- `models/pytorch_model.pth` is the selected model checkpoint for future inference and evaluation work.
- `images/` contains lightweight demo images.
- `docs/evaluation/classes.json` tracks the class names, RGB mask colors, and ignore index needed outside the ignored dataset directory.
- `docs/brainstorms/` and `docs/plans/` describe the product direction and implementation plan.

## Setup

Use Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The notebooks expect the Dubai satellite dataset at `DubaiDataset/`. That directory is intentionally ignored because it is a local data artifact, not a small source file.

Class metadata that future code and docs need is tracked separately in `docs/evaluation/classes.json`, so later work does not need to depend on ignored `DubaiDataset/classes.json` files.

## Model Artifact Policy

Only `models/pytorch_model.pth` is intentionally kept in this repository. Additional checkpoints are ignored by default.

Large model formats are marked for Git LFS in `.gitattributes`. If Git LFS is available in your environment, enable it before adding or replacing checkpoints:

```bash
git lfs install
git lfs track "*.pth" "*.pt" "*.ckpt" "*.onnx"
```

This worktree does not require extra checkpoints for the planned v1 demo.

## Planned Product Direction

The implementation plan in `docs/plans/2026-06-23-001-feat-satellite-demo-deployment-plan.md` breaks the next version into:

1. Repository hygiene and dependency baseline
2. Extracted PyTorch model and data utilities
3. Evaluation and demo artifact pipeline
4. FastAPI inference backend
5. Vercel frontend demo and case study
6. Deployment documentation
7. Portfolio and technical README rewrite
8. Public GitHub publication

The immediate next engineering step after this baseline is extracting notebook logic into reusable Python modules under `src/satseg/`.
