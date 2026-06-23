---
date: 2026-06-23
topic: satellite-segmentation-demo
---

# Satellite Segmentation Demo Requirements

## Summary

Build this project into a portfolio-quality satellite image segmentation demo that opens with an interactive experience and backs it up with a clear ML case study. The first version should make the PyTorch model path understandable, show segmentation results on uploaded and sample imagery, and explain evaluation quality without overclaiming model performance.

---

## Problem Frame

The project currently demonstrates the important pieces of a semantic segmentation workflow, but most of the value is locked inside notebooks and model files. A recruiter, classmate, or client can see that work exists, but they cannot quickly try the model, understand the model's strengths and weaknesses, or judge the project as a complete ML product.

The next version should turn the project into a credible portfolio artifact. It should feel polished enough to demo, but technical enough to show the model-building process and the evaluation judgment behind it.

---

## Key Decisions

- **Demo first, case study nearby.** The first viewport should prioritize trying or seeing the segmentation experience, with model details close enough that a serious reviewer can inspect the workflow.
- **Portfolio and learning audiences share priority.** The product should impress demo viewers while also teaching how the PyTorch training and evaluation path works.
- **Evaluation quality is the v1 model story.** The first model-improvement push should focus on better evaluation, per-class analysis, and failure cases rather than claiming the model has already improved.
- **Frontend and inference can deploy separately.** Vercel should host the web experience, while PyTorch inference may run in a separate backend suited to model serving.
- **README is both showcase and runbook.** The README should start with a portfolio-friendly overview, then provide enough setup, training, evaluation, and deployment detail for reproducibility.

---

## Actors

- A1. Demo viewer: a recruiter, classmate, client, or reviewer who wants to understand the project quickly and try the segmentation demo.
- A2. Technical reviewer: someone who wants evidence that the ML workflow, data split, metrics, and limitations were handled thoughtfully.
- A3. Project maintainer: the developer improving the PyTorch model path, keeping evaluation reproducible, and preparing the project for deployment.

---

## Requirements

**Interactive Demo**

- R1. The deployed experience must let a demo viewer run segmentation on a satellite image without understanding the notebook workflow.
- R2. The demo must support curated sample images with known outputs so the project remains inspectable even when a viewer does not have a suitable image to upload.
- R3. The result view must include a segmentation visualization, a class legend, and enough context to understand what the colors represent.
- R4. The app must communicate that results are a demo of a trained model, not authoritative geospatial analysis.

**ML Case Study**

- R5. The case study must explain the dataset, class labels, and PyTorch model path centered on `notebook/segmentation_pytorch.ipynb` and `models/pytorch_model.pth`.
- R6. The evaluation section must report per-class IoU so minority-class behavior is visible.
- R7. The evaluation section must compare validation and test metrics and explain why pixel accuracy can look strong while IoU exposes weaker segmentation quality.
- R8. The case study must include representative success and failure examples so viewers can see where the model performs well and where it struggles.

**Project Packaging**

- R9. The project must provide a hybrid README that serves both as a portfolio overview and as technical setup documentation.
- R10. The project must preserve reproducible local workflows for evaluation and inference before deployment polish is treated as complete.
- R11. The deployed frontend must be compatible with a Vercel-hosted web experience while allowing model inference to live in a separate backend.

---

## Key Flows

- F1. Try a sample image
  - **Trigger:** A demo viewer opens the deployed project and selects a curated sample.
  - **Actors:** A1
  - **Steps:** The viewer picks a sample, the app shows the original image, the segmentation output, and the class legend.
  - **Outcome:** The viewer understands the model output without needing their own image.
  - **Covered by:** R1, R2, R3, R4

- F2. Upload an image
  - **Trigger:** A demo viewer uploads a satellite-style image.
  - **Actors:** A1
  - **Steps:** The app accepts the image, sends it for inference, and displays the segmentation visualization with context.
  - **Outcome:** The viewer can interact with the model directly.
  - **Covered by:** R1, R3, R4, R11

- F3. Review model evidence
  - **Trigger:** A technical reviewer wants to understand whether the model is evaluated responsibly.
  - **Actors:** A2
  - **Steps:** The reviewer reads the case study, checks validation/test metrics, reviews per-class IoU, and inspects success/failure examples.
  - **Outcome:** The reviewer sees both the model's capabilities and its limitations.
  - **Covered by:** R5, R6, R7, R8

- F4. Reproduce the project locally
  - **Trigger:** A project maintainer or technical reviewer wants to run the project outside the hosted demo.
  - **Actors:** A2, A3
  - **Steps:** The reader follows the README to set up dependencies, understand the data/model paths, and run evaluation or inference locally.
  - **Outcome:** The project can be inspected and extended without relying only on the hosted app.
  - **Covered by:** R5, R9, R10

---

## Acceptance Examples

- AE1. Covers R1, R2, R3. Given a viewer has no local image, when they choose a curated sample, then the app displays the sample, segmentation output, and class legend.
- AE2. Covers R1, R3, R4. Given a viewer uploads a satellite-style image, when inference completes, then the app displays a segmentation result and labels it as model output rather than ground truth.
- AE3. Covers R6, R7. Given a reviewer opens the model evaluation section, when they compare validation and test results, then they can see per-class IoU and understand why pixel accuracy alone is not enough.
- AE4. Covers R8. Given the model has known weak cases, when a reviewer reads the case study, then at least one failure example is presented with a short explanation.
- AE5. Covers R9, R10. Given a developer clones the project, when they read the README, then they can identify the PyTorch notebook/model path, setup expectations, and local evaluation route.

---

## Success Criteria

- The deployed project can be understood in under one minute by a portfolio viewer.
- A technical reviewer can find model architecture, dataset, metrics, and limitations without opening the notebook first.
- Per-class IoU and validation/test comparison are present before the deployment is considered v1-ready.
- The README makes the project look polished while still being useful as a technical runbook.
- The app's claims stay aligned with demo-quality semantic segmentation, not production-grade geospatial analysis.

---

## Scope Boundaries

### In Scope for v1

- Interactive upload and curated-sample segmentation demo.
- Case-study content explaining dataset, classes, model path, metrics, and failure cases.
- Evaluation improvements centered on per-class IoU and clearer validation/test interpretation.
- Hybrid README rewrite.
- Vercel-hosted frontend with a separate inference backend when needed.

### Deferred for Later

- Model explainability features such as Grad-CAM or attention visualization.
- Stronger training improvements such as augmentation experiments, class imbalance handling, or architecture comparisons.
- Batch processing and larger imagery workflows after the demo proves useful.

### Outside This Product's Identity for v1

- User accounts, saved upload history, dashboards, or collaboration features.
- GeoTIFF processing, map tiling, coordinate systems, or full GIS workflows.
- Training or retraining models from the deployed app.
- Claims that the app provides authoritative land-use analysis.

---

## Dependencies and Assumptions

- The PyTorch path remains the primary model path for future work.
- `models/pytorch_model.pth` remains the main model artifact unless planning decides to retrain and replace it.
- The deployed inference backend must be able to run the PyTorch model within acceptable latency and resource limits.
- Curated sample images can be selected from existing project imagery or added as deployment-safe demo assets.

---

## Outstanding Questions

### Deferred to Planning

- Which backend target should serve PyTorch inference for the first deployment?
- Which sample images should ship with the demo, and how should their expected outputs be generated and stored?
- How should evaluation artifacts be generated so README, app, and case-study content do not drift?
- What is the minimum local command or script surface needed to make evaluation and inference reproducible outside notebooks?

---

## Sources and Research

- Current primary training path: `notebook/segmentation_pytorch.ipynb`
- Current primary model artifact: `models/pytorch_model.pth`
- Current project overview: `README.md`
- Dataset class metadata: `DubaiDataset/classes.json`
